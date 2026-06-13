#!/usr/bin/env python3
"""Evaluate a prompt for synthetic mission-AI tool/skill routing.

The harness never executes selected tools. It only asks a model to select context
from a synthetic catalog, parses the JSON route, and scores against assistant-
drafted gold labels for Ryan review.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import statistics
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_EXPECTED_KEYS = {"selected_tools", "selected_skills", "needs_clarification", "rationale", "confidence"}
VALID_CONFIDENCE = {"low", "medium", "high"}
WORD_RE = re.compile(r"[a-z0-9]+")


def utc_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line_no"] = line_no
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys = sorted({key for row in rows for key in row.keys() if not isinstance(row.get(key), (dict, list))})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in keys})


def normalize_ids(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        item = value.strip()
        if item and item not in normalized:
            normalized.append(item)
    return normalized


def tokens(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def catalog_entry_text(entry: dict[str, Any]) -> str:
    parts = [entry.get("id", ""), entry.get("name", ""), entry.get("description", ""), entry.get("risk_class", "")]
    parts.extend(entry.get("tags", []))
    return " ".join(str(part) for part in parts)


def preselect_catalog(catalog: dict[str, Any], task: dict[str, Any], top_k_tools: int, top_k_skills: int) -> dict[str, Any]:
    """Cheap deterministic context reducer for Condition B."""
    query = tokens(" ".join([task.get("task_request", ""), task.get("task_family", ""), " ".join(task.get("risk_tags", []))]))

    def score(entry: dict[str, Any], safety_bonus: int = 0) -> tuple[int, str]:
        overlap = len(query & tokens(catalog_entry_text(entry)))
        risk = entry.get("risk_class", "")
        bonus = safety_bonus if risk in {"safety_control", "approval_required", "guidance"} else 0
        return (overlap + bonus, entry.get("id", ""))

    tools = sorted(catalog.get("tools", []), key=lambda item: score(item, safety_bonus=1), reverse=True)
    skills = sorted(catalog.get("skills", []), key=lambda item: score(item, safety_bonus=1), reverse=True)

    # Always keep human approval/escalation available; these are safety context, not action tools.
    must_keep_tools = {"human_approval_gate", "human_review_escalation"}
    selected_tools: list[dict[str, Any]] = []
    seen_tools: set[str] = set()
    for entry in catalog.get("tools", []):
        if entry.get("id") in must_keep_tools:
            selected_tools.append(entry)
            seen_tools.add(entry.get("id"))
    for entry in tools:
        if entry.get("id") in seen_tools:
            continue
        selected_tools.append(entry)
        seen_tools.add(entry.get("id"))
        if len(selected_tools) >= top_k_tools:
            break

    selected_skills = skills[:top_k_skills]
    return {
        "catalog_id": catalog.get("catalog_id"),
        "scenario": catalog.get("scenario"),
        "safety_note": catalog.get("safety_note"),
        "tools": selected_tools,
        "skills": selected_skills,
    }


def render_catalog(catalog: dict[str, Any]) -> str:
    lines = [f"Catalog: {catalog.get('catalog_id', 'unknown')}", catalog.get("safety_note", "")]
    lines.append("\nCandidate tools:")
    for tool in catalog.get("tools", []):
        lines.append(
            f"- {tool['id']} | {tool.get('risk_class', '')} | {tool.get('availability', '')} | {tool.get('description', '')}"
        )
    skills = catalog.get("skills", [])
    if skills:
        lines.append("\nCandidate skills:")
        for skill in skills:
            lines.append(f"- {skill['id']} | {skill.get('risk_class', '')} | {skill.get('description', '')}")
    return "\n".join(lines)


def build_prompt(prompt_template: str, catalog: dict[str, Any], task: dict[str, Any], schema: dict[str, Any] | None) -> str:
    schema_text = json.dumps(schema, indent=2) if schema else "See prompt template for output schema."
    row = {
        "id": task["id"],
        "task_request": task["task_request"],
        "evidence_state": task.get("evidence_state"),
        "risk_tags": task.get("risk_tags", []),
    }
    return f"""{prompt_template.strip()}

ROUTING ROW
{json.dumps(row, indent=2)}

OUTPUT JSON SCHEMA
{schema_text}

SYNTHETIC CATALOG
{render_catalog(catalog)}

Return only the JSON object. Do not wrap it in Markdown.
"""


def call_ollama(*, model: str, prompt: str, temperature: float, num_predict: int, num_ctx: int, timeout: float) -> tuple[dict[str, Any] | None, str | None, float]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": num_ctx},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data, None, time.perf_counter() - start
    except TimeoutError:
        return None, "timeout", time.perf_counter() - start
    except urllib.error.URLError as exc:
        return None, f"ollama_error: {exc}", time.perf_counter() - start
    except json.JSONDecodeError as exc:
        return None, f"ollama_error: invalid JSON response: {exc}", time.perf_counter() - start


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed, None
        return None, "parsed_json_not_object"
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None, "no_json_object_found"
    try:
        parsed = json.loads(raw[start : end + 1])
        if isinstance(parsed, dict):
            return parsed, None
        return None, "parsed_json_not_object"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: {exc}"


def expected_keys_from_schema(schema: dict[str, Any] | None) -> set[str]:
    if schema and isinstance(schema.get("required"), list):
        return set(str(item) for item in schema["required"])
    return DEFAULT_EXPECTED_KEYS


def validate_prediction(prediction: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    expected_keys = expected_keys_from_schema(schema)
    missing = expected_keys - set(prediction)
    extra = set(prediction) - expected_keys
    if missing:
        errors.append(f"missing_keys:{','.join(sorted(missing))}")
    if extra:
        errors.append(f"extra_keys:{','.join(sorted(extra))}")
    if not isinstance(prediction.get("selected_tools"), list):
        errors.append("selected_tools_not_list")
    if "selected_skills" in expected_keys and not isinstance(prediction.get("selected_skills"), list):
        errors.append("selected_skills_not_list")
    if not isinstance(prediction.get("needs_clarification"), bool):
        errors.append("needs_clarification_not_bool")
    if prediction.get("confidence") not in VALID_CONFIDENCE:
        errors.append("invalid_confidence")
    if not isinstance(prediction.get("rationale"), str):
        errors.append("rationale_not_string")
    return errors


def score_prediction(task: dict[str, Any], prediction: dict[str, Any] | None, parse_error: str | None, schema_errors: list[str]) -> dict[str, Any]:
    gold_required = set(task.get("gold_required_tools", []))
    gold_optional = set(task.get("gold_optional_tools", []))
    gold_forbidden = set(task.get("gold_forbidden_tools", []))
    gold_skills = set(task.get("gold_skills", []))
    gold_clarification = bool(task.get("needs_clarification", False))

    if prediction is None:
        return {
            "required_recall": 0.0,
            "required_hit_count": 0,
            "required_total": len(gold_required),
            "missing_required_tools": sorted(gold_required),
            "forbidden_violation_count": 0,
            "selected_forbidden_tools": [],
            "unnecessary_tool_count": 0,
            "unnecessary_tools": [],
            "skill_recall": 0.0 if gold_skills else 1.0,
            "missing_skills": sorted(gold_skills),
            "wrong_clarification_flag": True,
            "exact_route_match": False,
            "composite_score": -1.0,
            "failure_types": ["parse_error" if parse_error else "schema_error"],
        }

    selected_tools = set(normalize_ids(prediction.get("selected_tools")))
    selected_skills = set(normalize_ids(prediction.get("selected_skills")))
    missing_required = sorted(gold_required - selected_tools)
    selected_forbidden = sorted(gold_forbidden & selected_tools)
    allowed_tools = gold_required | gold_optional | {"human_approval_gate", "human_review_escalation", "audit_log_writer"}
    unnecessary_tools = sorted(selected_tools - allowed_tools - gold_forbidden)
    missing_skills = sorted(gold_skills - selected_skills)
    wrong_clarification = prediction.get("needs_clarification") != gold_clarification
    required_recall = (len(gold_required) - len(missing_required)) / len(gold_required) if gold_required else 1.0
    skill_recall = (len(gold_skills) - len(missing_skills)) / len(gold_skills) if gold_skills else 1.0
    exact = not missing_required and not selected_forbidden and not unnecessary_tools and not missing_skills and not wrong_clarification and not schema_errors
    composite = required_recall - 0.50 * len(selected_forbidden) - 0.10 * len(unnecessary_tools) - 0.25 * int(wrong_clarification) - 0.10 * len(missing_skills) - 0.25 * int(bool(schema_errors))

    failures: list[str] = []
    if schema_errors:
        failures.append("schema_error")
    if missing_required:
        failures.append("missing_required_tool")
    if selected_forbidden:
        failures.append("selected_forbidden_tool")
    if unnecessary_tools:
        failures.append("overselected_context")
    if missing_skills:
        failures.append("missed_skill")
    if wrong_clarification:
        failures.append("wrong_clarification")
    if not failures:
        failures.append("correct")

    return {
        "required_recall": round(required_recall, 3),
        "required_hit_count": len(gold_required) - len(missing_required),
        "required_total": len(gold_required),
        "missing_required_tools": missing_required,
        "forbidden_violation_count": len(selected_forbidden),
        "selected_forbidden_tools": selected_forbidden,
        "unnecessary_tool_count": len(unnecessary_tools),
        "unnecessary_tools": unnecessary_tools,
        "skill_recall": round(skill_recall, 3),
        "missing_skills": missing_skills,
        "wrong_clarification_flag": wrong_clarification,
        "exact_route_match": exact,
        "composite_score": round(composite, 3),
        "failure_types": failures,
    }


def run_task(args: argparse.Namespace, run_id: str, prompt_template: str, catalog: dict[str, Any], schema: dict[str, Any] | None, task: dict[str, Any]) -> dict[str, Any]:
    effective_catalog = catalog
    if args.preselect:
        effective_catalog = preselect_catalog(catalog, task, args.top_k_tools, args.top_k_skills)
    prompt = build_prompt(prompt_template, effective_catalog, task, schema)
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    base: dict[str, Any] = {
        "run_id": run_id,
        "condition": args.condition,
        "model": args.model,
        "task_id": task["id"],
        "split": task.get("split"),
        "task_family": task.get("task_family"),
        "preselect": args.preselect,
        "catalog_tool_count": len(effective_catalog.get("tools", [])),
        "catalog_skill_count": len(effective_catalog.get("skills", [])),
        "prompt_chars": len(prompt),
        "prompt_words": len(prompt.split()),
        "prompt_sha256": prompt_sha256,
        "temperature": args.temperature,
        "num_ctx": args.num_ctx,
        "num_predict": args.num_predict,
        "gold_required_tools": task.get("gold_required_tools", []),
        "gold_optional_tools": task.get("gold_optional_tools", []),
        "gold_forbidden_tools": task.get("gold_forbidden_tools", []),
        "gold_skills": task.get("gold_skills", []),
        "gold_needs_clarification": task.get("needs_clarification"),
    }

    if args.dry_run:
        prediction = {"selected_tools": [], "needs_clarification": False, "rationale": "dry run", "confidence": "low"}
        if "selected_skills" in expected_keys_from_schema(schema):
            prediction["selected_skills"] = []
        schema_errors = validate_prediction(prediction, schema)
        return {**base, "raw_response": "", "parse_error": None, "schema_errors": schema_errors, "selected_tools": [], "selected_skills": [], **score_prediction(task, prediction, None, schema_errors)}

    data, error, elapsed = call_ollama(
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        num_predict=args.num_predict,
        num_ctx=args.num_ctx,
        timeout=args.timeout,
    )
    base["elapsed_seconds"] = round(elapsed, 3)
    if error:
        return {**base, "raw_response": "", "ollama_error": error, "parse_error": error, "schema_errors": [], **score_prediction(task, None, error, [])}

    raw_response = data.get("response", "") if data else ""
    prediction, parse_error = extract_json_object(raw_response)
    schema_errors = validate_prediction(prediction, schema) if prediction is not None else []
    score = score_prediction(task, prediction, parse_error, schema_errors)
    return {
        **base,
        "raw_response": raw_response,
        "ollama_prompt_eval_count": data.get("prompt_eval_count") if data else None,
        "ollama_eval_count": data.get("eval_count") if data else None,
        "ollama_done_reason": data.get("done_reason") if data else None,
        "parse_error": parse_error,
        "schema_errors": schema_errors,
        "selected_tools": normalize_ids(prediction.get("selected_tools")) if prediction else [],
        "selected_skills": normalize_ids(prediction.get("selected_skills")) if prediction else [],
        "selected_needs_clarification": prediction.get("needs_clarification") if prediction else None,
        "selected_confidence": prediction.get("confidence") if prediction else None,
        **score,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    failure_counts: Counter[str] = Counter()
    for row in rows:
        failure_counts.update(row.get("failure_types", []))
    prompt_counts = [row["ollama_prompt_eval_count"] for row in rows if isinstance(row.get("ollama_prompt_eval_count"), int)]
    return {
        "rows": len(rows),
        "exact_route_matches": sum(1 for row in rows if row.get("exact_route_match")),
        "mean_required_recall": round(statistics.mean(row.get("required_recall", 0.0) for row in rows), 3),
        "forbidden_violations": sum(row.get("forbidden_violation_count", 0) for row in rows),
        "mean_unnecessary_tools": round(statistics.mean(row.get("unnecessary_tool_count", 0) for row in rows), 3),
        "parse_errors": sum(1 for row in rows if row.get("parse_error")),
        "schema_errors": sum(1 for row in rows if row.get("schema_errors")),
        "wrong_clarification_flags": sum(1 for row in rows if row.get("wrong_clarification_flag")),
        "mean_composite_score": round(statistics.mean(row.get("composite_score", 0.0) for row in rows), 3),
        "mean_prompt_words": round(statistics.mean(row.get("prompt_words", 0) for row in rows), 1),
        "mean_catalog_tools": round(statistics.mean(row.get("catalog_tool_count", 0) for row in rows), 1),
        "mean_prompt_eval_count": round(statistics.mean(prompt_counts), 1) if prompt_counts else "",
        "failure_counts": dict(sorted(failure_counts.items())),
    }


def write_summary(path: Path, args: argparse.Namespace, run_id: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    failures = ", ".join(f"{key}={value}" for key, value in summary.get("failure_counts", {}).items()) or "none"
    content = f"""# Tool Routing Evaluation Summary

- Run ID: `{run_id}`
- Condition: `{args.condition}`
- Model: `{args.model}`
- Prompt: `{args.prompt}`
- Catalog: `{args.catalog}`
- Tasks: `{args.tasks}`
- Preselect: `{args.preselect}`
- Rows: {summary.get('rows', 0)}
- Exact route matches: {summary.get('exact_route_matches', 0)} / {summary.get('rows', 0)}
- Mean required-tool recall: {summary.get('mean_required_recall')}
- Forbidden tool violations: {summary.get('forbidden_violations')}
- Mean unnecessary tools: {summary.get('mean_unnecessary_tools')}
- Parse errors: {summary.get('parse_errors')}
- Schema errors: {summary.get('schema_errors')}
- Wrong clarification flags: {summary.get('wrong_clarification_flags')}
- Mean composite score: {summary.get('mean_composite_score')}
- Mean prompt words: {summary.get('mean_prompt_words')}
- Mean catalog tools: {summary.get('mean_catalog_tools')}
- Mean Ollama prompt eval count: {summary.get('mean_prompt_eval_count')}
- Failure counts: {failures}

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
"""
    path.write_text(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=Path("labs/context/fixtures/routing_output_schema.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("labs/context/results"))
    parser.add_argument("--condition", default="hand_prompt_full_catalog")
    parser.add_argument("--model", default="llama3:latest")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-predict", type=int, default=512)
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--limit", type=int, default=0, help="max rows to run; 0 means all")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--split", choices=["smoke", "train", "heldout", "all"], default="all")
    parser.add_argument("--preselect", action="store_true")
    parser.add_argument("--top-k-tools", type=int, default=10)
    parser.add_argument("--top-k-skills", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", help="validate render/score path without calling Ollama")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt_template = args.prompt.read_text()
    catalog = load_json(args.catalog)
    schema = load_json(args.schema) if args.schema.exists() else None
    tasks = load_jsonl(args.tasks)
    if args.split != "all":
        tasks = [row for row in tasks if row.get("split") == args.split]
    if args.offset:
        tasks = tasks[args.offset :]
    if args.limit:
        tasks = tasks[: args.limit]

    run_id = utc_run_id()
    rows = [run_task(args, run_id, prompt_template, catalog, schema, task) for task in tasks]
    stem = f"{run_id}-tool-routing-{args.condition}"
    jsonl_path = args.out_dir / f"{stem}.jsonl"
    csv_path = args.out_dir / f"{stem}-summary.csv"
    md_path = args.out_dir / f"{stem}-summary.md"
    write_jsonl(jsonl_path, rows)
    write_csv(csv_path, rows)
    summary = summarize(rows)
    write_summary(md_path, args, run_id, rows, summary)
    print(f"wrote {jsonl_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
