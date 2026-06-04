#!/usr/bin/env python3
"""Run the recruiter-screen few-shot order-sensitivity lab.

This script is intentionally standard-library only so the public course repo stays
lightweight. It writes raw JSONL rows plus CSV/Markdown summaries.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LABELS = {"technical_screen", "no_technical_screen"}
CONFIDENCE = {"low", "medium", "high"}
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/chat"


class FixtureError(ValueError):
    pass


def utc_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    validate_fixture(data)
    return data


def validate_fixture(data: dict[str, Any]) -> None:
    labels = set(data.get("labels", []))
    if labels != LABELS:
        raise FixtureError(f"Fixture labels must be exactly {sorted(LABELS)}, got {sorted(labels)}")

    examples = data.get("examples") or []
    candidates = data.get("candidates") or []
    variants = data.get("order_variants") or []
    if not examples:
        raise FixtureError("Fixture has no examples")
    if not candidates:
        raise FixtureError("Fixture has no candidates")
    if not variants:
        raise FixtureError("Fixture has no order variants")

    example_by_id: dict[str, dict[str, Any]] = {}
    for ex in examples:
        eid = ex.get("id")
        if not eid or eid in example_by_id:
            raise FixtureError(f"Missing or duplicate example id: {eid!r}")
        if ex.get("label") not in LABELS:
            raise FixtureError(f"Example {eid} has invalid label {ex.get('label')!r}")
        for key in ("summary", "rationale"):
            if not ex.get(key):
                raise FixtureError(f"Example {eid} missing {key}")
        example_by_id[eid] = ex

    for variant in variants:
        vid = variant.get("id")
        ids = variant.get("example_ids") or []
        if not vid:
            raise FixtureError("Order variant missing id")
        if set(ids) != set(example_by_id):
            raise FixtureError(f"Variant {vid} must reference each example exactly once")
        if len(ids) != len(set(ids)):
            raise FixtureError(f"Variant {vid} repeats an example id")

    candidate_ids: set[str] = set()
    for cand in candidates:
        cid = cand.get("id")
        if not cid or cid in candidate_ids:
            raise FixtureError(f"Missing or duplicate candidate id: {cid!r}")
        if not cand.get("band") or not cand.get("summary"):
            raise FixtureError(f"Candidate {cid} missing band or summary")
        candidate_ids.add(cid)


def selected(items: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    return items[:limit] if limit else items


def render_prompt(
    fixture: dict[str, Any], variant: dict[str, Any], candidate: dict[str, Any]
) -> str:
    examples_by_id = {ex["id"]: ex for ex in fixture["examples"]}
    ordered_examples = [examples_by_id[eid] for eid in variant["example_ids"]]
    rubric = fixture["rubric"]

    lines: list[str] = []
    lines.append("You are classifying FICTIONAL candidate summaries for a synthetic prompt-engineering lab.")
    lines.append("This is not a real hiring tool. Do not infer protected traits or private facts.")
    lines.append("Target role: generic technical role.")
    lines.append("Return only one compact JSON object. No markdown, no code fence, no extra text.")
    lines.append("")
    lines.append("Allowed labels: technical_screen, no_technical_screen")
    lines.append("")
    lines.append("Rubric: advance to technical_screen when the summary shows at least two of:")
    for item in rubric["advance_when_at_least_two"]:
        lines.append(f"- {item}")
    lines.append("Use no_technical_screen when the summary mostly shows:")
    for item in rubric["do_not_advance_when_mostly"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Few-shot examples:")
    for idx, ex in enumerate(ordered_examples, start=1):
        lines.append(f"Example {idx} summary: {ex['summary']}")
        lines.append(f"Example {idx} JSON: {json.dumps({'label': ex['label'], 'confidence': 'high', 'rationale': ex['rationale']}, ensure_ascii=False)}")
    lines.append("")
    lines.append(f"Candidate to classify ({candidate['id']}): {candidate['summary']}")
    lines.append("")
    lines.append("Output schema:")
    lines.append('{"label":"technical_screen|no_technical_screen","confidence":"low|medium|high","rationale":"one sentence"}')
    return "\n".join(lines)


def parse_response(raw: str) -> tuple[str | None, str | None, str | None, str]:
    text = raw.strip()
    if not text:
        return None, None, None, "empty_response"

    # Remove common code fences without treating them as success by themselves.
    unfenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()

    candidates = [unfenced]
    match = re.search(r"\{[\s\S]*\}", unfenced)
    if match:
        candidates.append(match.group(0))

    for blob in candidates:
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            label = obj.get("label")
            confidence = obj.get("confidence")
            rationale = obj.get("rationale")
            if label in LABELS:
                if confidence not in CONFIDENCE:
                    confidence = None
                if rationale is not None and not isinstance(rationale, str):
                    rationale = str(rationale)
                return label, confidence, rationale, "json_ok"
            return None, confidence if confidence in CONFIDENCE else None, str(rationale) if rationale else None, "json_invalid_label"

    found = [label for label in LABELS if re.search(rf"\b{re.escape(label)}\b", unfenced)]
    if len(found) == 1:
        return found[0], None, None, "label_fallback"
    if len(found) > 1:
        return None, None, None, "ambiguous_label_fallback"
    return None, None, None, "invalid_response"


def truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"


def call_ollama(model: str, prompt: str, temperature: float, timeout: int, num_predict: int, url: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only valid JSON matching the requested schema."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": num_predict},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        latency = time.time() - started
        data = json.loads(body)
        message = data.get("message") or {}
        content = message.get("content") or data.get("response") or ""
        usage = {k: data.get(k) for k in ("total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration") if k in data}
        return {"raw": content, "latency_seconds": latency, "usage": usage, "error": None}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"raw": "", "latency_seconds": time.time() - started, "usage": {}, "error": f"ollama_error: {exc}"}


def call_codex(model: str, prompt: str, timeout: int) -> dict[str, Any]:
    # Codex writes the final assistant message to a temp file, reducing terminal UI noise.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "label": {"type": "string", "enum": sorted(LABELS)},
            "confidence": {"type": "string", "enum": sorted(CONFIDENCE)},
            "rationale": {"type": "string"},
        },
        "required": ["label", "confidence", "rationale"],
    }
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="recruiter-screen-codex-") as tmp:
        tmp_path = Path(tmp)
        out_path = tmp_path / "last_message.json"
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        full_prompt = (
            "Classify this one synthetic candidate. Return only the final JSON object. "
            "Do not inspect or edit repository files.\n\n" + prompt
        )
        cmd = [
            "codex",
            "exec",
            "--model",
            model,
            "-c",
            'model_reasoning_effort="xhigh"',
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(out_path),
            full_prompt,
        ]
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
        except FileNotFoundError as exc:
            return {"raw": "", "latency_seconds": time.time() - started, "usage": {}, "error": f"codex_not_found: {exc}"}
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            return {
                "raw": truncate(str(stdout) + "\n" + str(stderr), 4000),
                "latency_seconds": time.time() - started,
                "usage": {},
                "error": f"codex_timeout_after_{timeout}s",
            }
        raw = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else proc.stdout
        error = None
        if proc.returncode != 0:
            error = f"codex_exit_{proc.returncode}: {truncate(proc.stderr or proc.stdout, 1000)}"
        return {"raw": raw, "latency_seconds": time.time() - started, "usage": {"returncode": proc.returncode}, "error": error}


def call_model(adapter: str, model: str, prompt: str, args: argparse.Namespace) -> dict[str, Any]:
    if adapter == "ollama":
        return call_ollama(model, prompt, args.temperature, args.timeout, args.num_predict, args.ollama_url)
    if adapter == "codex":
        return call_codex(model, prompt, args.timeout)
    return {"raw": "", "latency_seconds": 0.0, "usage": {}, "error": f"unsupported_adapter: {adapter}"}


def model_specs(spec: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in [part.strip() for part in spec.split(",") if part.strip()]:
        if ":" not in item:
            raise ValueError(f"Model spec must be adapter:model, got {item!r}")
        adapter, model = item.split(":", 1)
        if adapter not in {"ollama", "codex"}:
            raise ValueError(f"Unsupported adapter {adapter!r}")
        pairs.append((adapter, model))
    if not pairs:
        raise ValueError("At least one model is required")
    return pairs


def build_row(
    run_id: str,
    adapter: str,
    model: str,
    variant: dict[str, Any],
    candidate: dict[str, Any],
    repeat: int,
    temperature: float,
    prompt: str,
    response: dict[str, Any],
) -> dict[str, Any]:
    label, confidence, rationale, parse_status = parse_response(response.get("raw") or "")
    return {
        "run_id": run_id,
        "model_adapter": adapter,
        "model": model,
        "candidate_id": candidate["id"],
        "candidate_band": candidate["band"],
        "order_variant": variant["id"],
        "order_description": variant.get("description"),
        "repeat": repeat,
        "temperature": temperature,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "raw_response_truncated": truncate(response.get("raw") or ""),
        "parsed_label": label,
        "confidence": confidence,
        "rationale": rationale,
        "parse_status": parse_status,
        "latency_seconds": round(float(response.get("latency_seconds") or 0.0), 3),
        "usage": response.get("usage") or {},
        "error": response.get("error"),
    }


def summarize(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model_adapter"], row["model"], row["candidate_id"])].append(row)

    summary_rows: list[dict[str, Any]] = []
    for (adapter, model, candidate_id), items in sorted(grouped.items()):
        labels = [row["parsed_label"] for row in items if row.get("parsed_label")]
        unique = sorted(set(labels))
        bands = sorted({row["candidate_band"] for row in items})
        invalid = sum(1 for row in items if row.get("parse_status") != "json_ok" and row.get("parse_status") != "label_fallback")
        errors = sum(1 for row in items if row.get("error"))
        summary_rows.append(
            {
                "model_adapter": adapter,
                "model": model,
                "candidate_id": candidate_id,
                "candidate_band": bands[0] if bands else "unknown",
                "attempted": len(items),
                "parsed": len(labels),
                "invalid_or_unparsed": invalid,
                "errors": errors,
                "labels_observed": ";".join(unique),
                "is_order_sensitive": len(unique) > 1,
                "flip_count": max(0, len(unique) - 1),
            }
        )

    by_model = Counter((row["model_adapter"], row["model"]) for row in rows)
    invalid_by_model = Counter((row["model_adapter"], row["model"]) for row in rows if not row.get("parsed_label"))
    errors_by_model = Counter((row["model_adapter"], row["model"]) for row in rows if row.get("error"))
    flips_by_band = Counter(row["candidate_band"] for row in summary_rows if row["is_order_sensitive"])
    candidates_by_band = Counter(row["candidate_band"] for row in summary_rows)

    total_flips = sum(1 for row in summary_rows if row["is_order_sensitive"])
    total_invalid = sum(1 for row in rows if not row.get("parsed_label"))
    if total_invalid:
        interpretation = "invalid_outputs_prevent_claim"
    elif total_flips == 0:
        interpretation = "no_flips_observed"
    elif total_flips == flips_by_band.get("borderline", 0):
        interpretation = "borderline_only_flips"
    else:
        interpretation = "broad_instability_observed"

    aggregate = {
        "total_rows": len(rows),
        "by_model": {"/".join(k): v for k, v in by_model.items()},
        "invalid_by_model": {"/".join(k): v for k, v in invalid_by_model.items()},
        "errors_by_model": {"/".join(k): v for k, v in errors_by_model.items()},
        "flips_by_band": dict(flips_by_band),
        "candidates_by_band": dict(candidates_by_band),
        "interpretation": interpretation,
    }
    return summary_rows, aggregate


def write_outputs(rows: list[dict[str, Any]], out_dir: Path, run_id: str) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{run_id}-recruiter-screen-order-sensitivity"
    jsonl_path = out_dir / f"{base}.jsonl"
    csv_path = out_dir / f"{base}-summary.csv"
    md_path = out_dir / f"{base}-summary.md"

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary_rows, aggregate = summarize(rows)
    fieldnames = [
        "model_adapter",
        "model",
        "candidate_id",
        "candidate_band",
        "attempted",
        "parsed",
        "invalid_or_unparsed",
        "errors",
        "labels_observed",
        "is_order_sensitive",
        "flip_count",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# Recruiter-screen order-sensitivity summary\n\n")
        f.write(f"- Run ID: `{run_id}`\n")
        f.write(f"- Total rows: {aggregate['total_rows']}\n")
        f.write(f"- Interpretation: `{aggregate['interpretation']}`\n")
        f.write(f"- Rows by model: `{json.dumps(aggregate['by_model'], sort_keys=True)}`\n")
        f.write(f"- Invalid/unparsed by model: `{json.dumps(aggregate['invalid_by_model'], sort_keys=True)}`\n")
        f.write(f"- Errors by model: `{json.dumps(aggregate['errors_by_model'], sort_keys=True)}`\n")
        f.write(f"- Flips by band: `{json.dumps(aggregate['flips_by_band'], sort_keys=True)}`\n\n")
        f.write("| Model | Candidate | Band | Parsed/Attempted | Labels observed | Order sensitive | Errors |\n")
        f.write("|---|---|---|---:|---|---:|---:|\n")
        for row in summary_rows:
            model_name = f"{row['model_adapter']}:{row['model']}"
            f.write(
                f"| `{model_name}` | `{row['candidate_id']}` | {row['candidate_band']} | "
                f"{row['parsed']}/{row['attempted']} | `{row['labels_observed']}` | "
                f"{str(row['is_order_sensitive']).lower()} | {row['errors']} |\n"
            )

    return jsonl_path, csv_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--models", default="ollama:gpt-oss:20b")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--candidate-limit", type=int)
    parser.add_argument("--variant-limit", type=int)
    parser.add_argument("--out-dir", type=Path, default=Path("labs/prompt/results"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--num-predict", type=int, default=1024)
    parser.add_argument("--ollama-url", default=os.environ.get("OLLAMA_CHAT_URL", DEFAULT_OLLAMA_URL))
    args = parser.parse_args(argv)

    fixture = load_fixture(args.fixture)
    variants = selected(fixture["order_variants"], args.variant_limit)
    candidates = selected(fixture["candidates"], args.candidate_limit)
    models = model_specs(args.models)
    total_prompts = len(models) * len(variants) * len(candidates) * args.repeats

    if args.dry_run:
        print(
            json.dumps(
                {
                    "fixture": str(args.fixture),
                    "models": [f"{a}:{m}" for a, m in models],
                    "variants": [v["id"] for v in variants],
                    "candidate_count": len(candidates),
                    "repeat_count": args.repeats,
                    "prompt_count": total_prompts,
                    "dry_run": True,
                },
                indent=2,
            )
        )
        # Render one prompt to catch formatting bugs but do not print it by default.
        render_prompt(fixture, variants[0], candidates[0])
        return 0

    run_id = utc_run_id()
    rows: list[dict[str, Any]] = []
    attempted = 0
    for adapter, model in models:
        for repeat in range(1, args.repeats + 1):
            for variant in variants:
                for candidate in candidates:
                    attempted += 1
                    prompt = render_prompt(fixture, variant, candidate)
                    print(
                        f"[{attempted}/{total_prompts}] {adapter}:{model} {variant['id']} {candidate['id']} repeat={repeat}",
                        flush=True,
                    )
                    response = call_model(adapter, model, prompt, args)
                    row = build_row(run_id, adapter, model, variant, candidate, repeat, args.temperature, prompt, response)
                    rows.append(row)
                    if row.get("error"):
                        print(f"  error: {row['error']}", file=sys.stderr, flush=True)
                    else:
                        print(f"  parsed={row['parsed_label']} status={row['parse_status']} latency={row['latency_seconds']}s", flush=True)

    jsonl_path, csv_path, md_path = write_outputs(rows, args.out_dir, run_id)
    _, aggregate = summarize(rows)
    print(json.dumps({"jsonl": str(jsonl_path), "csv": str(csv_path), "markdown": str(md_path), **aggregate}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
