#!/usr/bin/env python3
"""Run the mission-AI tool-routing task as a DSPy typed module.

This is the Context Module 09 counterpart to the plain prompt evaluator. It uses
DSPy to define the router as a small declarative program, then reuses the same
fixture/scoring logic from evaluate_tool_routing_prompt.py. The script never
executes selected tools.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import dspy
except ImportError as exc:  # pragma: no cover - exercised by environment, not unit tests
    raise SystemExit(
        "DSPy is not installed. Create the lab venv with: "
        "python3 -m venv /tmp/agent-harness-dspy-venv && "
        "/tmp/agent-harness-dspy-venv/bin/python -m pip install 'dspy>=3.0.0'"
    ) from exc

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from evaluate_tool_routing_prompt import (  # noqa: E402
    build_prompt,
    load_json,
    load_jsonl,
    normalize_ids,
    preselect_catalog,
    render_catalog,
    score_prediction,
    summarize,
    utc_run_id,
    validate_prediction,
    write_csv,
    write_jsonl,
    write_summary,
)


class RouteTools(dspy.Signature):
    """Select the minimal safe tool context for a synthetic mission-brief request."""

    task_request: str = dspy.InputField(desc="The user's synthetic mission-support request.")
    evidence_state: str = dspy.InputField(desc="Whether evidence is provided, inline_only, missing, conflicting, or sensitive.")
    risk_tags: str = dspy.InputField(desc="Risk and handling tags for the request.")
    catalog: str = dspy.InputField(desc="Candidate tool catalog. Use ids exactly as written.")
    output_schema: str = dspy.InputField(desc="Required JSON object schema.")
    routing_json: str = dspy.OutputField(
        desc="Only a JSON object with selected_tools, needs_clarification, rationale, and confidence."
    )


class ToolRouter(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.route = dspy.Predict(RouteTools)

    def forward(self, task_request: str, evidence_state: str, risk_tags: str, catalog: str, output_schema: str) -> dspy.Prediction:
        return self.route(
            task_request=task_request,
            evidence_state=evidence_state,
            risk_tags=risk_tags,
            catalog=catalog,
            output_schema=output_schema,
        )


def extract_json(text: str) -> tuple[dict[str, Any] | None, str | None]:
    from evaluate_tool_routing_prompt import extract_json_object

    return extract_json_object(text)


def run_task(args: argparse.Namespace, router: ToolRouter, catalog: dict[str, Any], schema: dict[str, Any], task: dict[str, Any], run_id: str) -> dict[str, Any]:
    effective_catalog = catalog
    if args.preselect:
        effective_catalog = preselect_catalog(catalog, task, args.top_k_tools, args.top_k_skills)
    catalog_text = render_catalog(effective_catalog)
    schema_text = json.dumps(schema, indent=2)
    risk_tags = ", ".join(task.get("risk_tags", []))

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
        "prompt_words": len((task["task_request"] + risk_tags + catalog_text + schema_text).split()),
        "gold_required_tools": task.get("gold_required_tools", []),
        "gold_optional_tools": task.get("gold_optional_tools", []),
        "gold_forbidden_tools": task.get("gold_forbidden_tools", []),
        "gold_skills": task.get("gold_skills", []),
        "gold_needs_clarification": task.get("needs_clarification"),
    }

    try:
        prediction_obj = router(
            task_request=task["task_request"],
            evidence_state=str(task.get("evidence_state", "unknown")),
            risk_tags=risk_tags,
            catalog=catalog_text,
            output_schema=schema_text,
        )
        raw = str(prediction_obj.routing_json)
        prediction, parse_error = extract_json(raw)
        schema_errors = validate_prediction(prediction, schema) if prediction is not None else []
        score = score_prediction(task, prediction, parse_error, schema_errors)
        return {
            **base,
            "raw_response": raw,
            "parse_error": parse_error,
            "schema_errors": schema_errors,
            "selected_tools": normalize_ids(prediction.get("selected_tools")) if prediction else [],
            "selected_skills": normalize_ids(prediction.get("selected_skills")) if prediction else [],
            "selected_needs_clarification": prediction.get("needs_clarification") if prediction else None,
            "selected_confidence": prediction.get("confidence") if prediction else None,
            **score,
        }
    except Exception as exc:  # noqa: BLE001 - row-level failure should not crash the run
        return {
            **base,
            "raw_response": "",
            "parse_error": f"dspy_error: {type(exc).__name__}: {exc}",
            "schema_errors": [],
            **score_prediction(task, None, str(exc), []),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=Path("labs/context/fixtures/routing_output_schema.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("labs/context/results"))
    parser.add_argument("--condition", default="dspy_uncompiled_full_catalog")
    parser.add_argument("--model", default="ollama_chat/llama3:latest")
    parser.add_argument("--api-base", default="http://localhost:11434")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--split", choices=["smoke", "train", "heldout", "all"], default="all")
    parser.add_argument("--preselect", action="store_true")
    parser.add_argument("--top-k-tools", type=int, default=10)
    parser.add_argument("--top-k-skills", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    tasks = load_jsonl(args.tasks)
    if args.split != "all":
        tasks = [row for row in tasks if row.get("split") == args.split]
    if args.offset:
        tasks = tasks[args.offset :]
    if args.limit:
        tasks = tasks[: args.limit]

    lm = dspy.LM(args.model, api_base=args.api_base, temperature=args.temperature, max_tokens=args.max_tokens)
    dspy.configure(lm=lm)
    router = ToolRouter()

    run_id = utc_run_id()
    rows = [run_task(args, router, catalog, schema, task, run_id) for task in tasks]
    stem = f"{run_id}-tool-routing-{args.condition}"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / f"{stem}.jsonl"
    csv_path = args.out_dir / f"{stem}-summary.csv"
    md_path = args.out_dir / f"{stem}-summary.md"
    write_jsonl(jsonl_path, rows)
    write_csv(csv_path, rows)
    summary = summarize(rows)
    # Reuse the plain evaluator's summary writer by attaching compatible path-like attrs.
    setattr(args, "prompt", "DSPy Signature: RouteTools")
    write_summary(md_path, args, run_id, rows, summary)
    print(f"wrote {jsonl_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
