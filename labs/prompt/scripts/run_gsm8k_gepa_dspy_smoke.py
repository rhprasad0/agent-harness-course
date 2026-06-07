#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Tiny reliability-first DSPy/GEPA smoke test on GSM8K via local Ollama.

This is intentionally a learning smoke test, not the full Module 10 result.
It verifies the DSPy mental model in code:

- define an explicit structured LM program,
- separate format/adapter failures from math failures,
- define a metric that returns score + textual feedback,
- let GEPA try reflective prompt mutation,
- compare before/after on a tiny validation slice.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import dspy

DEFAULT_DATA = "labs/prompt/data/gsm8k/test.jsonl"
DEFAULT_RESULTS_DIR = "labs/prompt/results"
DEFAULT_MODEL = "mistral:7b-instruct-q4_K_M"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"


def normalize_numeric(text: Any | None) -> str | None:
    """Return a stable numeric string from messy prose, or None if no value exists."""
    if text is None:
        return None
    s = str(text).strip().replace(",", "").replace("$", "")
    matches = re.findall(r"[-+$]?[0-9][0-9,]*(?:\.[0-9]+)?", s)
    if matches:
        s = matches[-1].replace(",", "").replace("$", "")
    if not s:
        return None
    try:
        d = Decimal(s)
    except InvalidOperation:
        return s.lower()
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def normalize_integer(text: Any | None) -> int | None:
    normalized = normalize_numeric(text)
    if normalized is None:
        return None
    try:
        d = Decimal(normalized)
    except InvalidOperation:
        return None
    if d != d.to_integral_value():
        return None
    return int(d)


def gold_answer(answer: str) -> str:
    if "####" not in answer:
        raise ValueError("GSM8K answer is missing final-answer marker '####'")
    return answer.split("####", 1)[1].strip()


def load_examples(path: Path, *, offset: int, limit: int) -> list[dspy.Example]:
    examples: list[dspy.Example] = []
    with path.open("r", encoding="utf-8") as f:
        for row_index, line in enumerate(f, start=1):
            if row_index <= offset:
                continue
            if len(examples) >= limit:
                break
            row = json.loads(line)
            answer = normalize_integer(gold_answer(row["answer"]))
            if answer is None:
                raise ValueError(f"Could not parse integer gold answer for row {row_index}")
            examples.append(
                dspy.Example(
                    row_number=row_index,
                    question=row["question"],
                    answer=answer,
                    solution=row["answer"],
                ).with_inputs("question")
            )
    return examples


class GSM8KStructuredSignature(dspy.Signature):
    """Solve a grade-school math word problem. Compute carefully and return a clean structured answer."""

    question: str = dspy.InputField(desc="GSM8K math word problem")
    reasoning: str = dspy.OutputField(
        desc="brief arithmetic reasoning; include only steps needed to justify the final answer"
    )
    answer: int = dspy.OutputField(desc="final integer answer only; no units, commas, words, or equations")


class GSM8KStructuredSolver(dspy.Module):
    """Reliability-first GSM8K solver with explicit, typed output fields.

    We use Predict over an explicit reasoning+answer signature instead of ChainOfThought
    so the output schema is visible and stable. ChainOfThought implicitly prepends a
    rationale field, which is useful but noisier for this lab's adapter-reliability work.
    """

    def __init__(self) -> None:
        super().__init__()
        self.solve = dspy.Predict(GSM8KStructuredSignature)

    def forward(self, question: str) -> dspy.Prediction:
        pred = self.solve(question=question)
        return dspy.Prediction(
            reasoning=getattr(pred, "reasoning", None),
            answer=getattr(pred, "answer", None),
        )


# Backward-compatible aliases for older artifacts/imports.
GSM8KSignature = GSM8KStructuredSignature
GSM8KSolver = GSM8KStructuredSolver


def make_adapter(name: str) -> Any:
    normalized = name.strip().lower()
    if normalized == "chat":
        return dspy.ChatAdapter()
    if normalized == "json":
        return dspy.JSONAdapter()
    raise ValueError(f"Unsupported adapter {name!r}; expected 'chat' or 'json'")


def classify_prediction(example: dspy.Example, prediction: Any) -> dspy.Prediction:
    raw_answer = getattr(prediction, "answer", None)
    gold = int(example.answer)

    if isinstance(raw_answer, bool) or not isinstance(raw_answer, int):
        return dspy.Prediction(
            score=0.0,
            failure_type="format",
            parsed_answer=None,
            feedback=(
                "Format failure: the `answer` field must be an integer, not prose, a decimal, "
                f"a missing value, or another type. Received {raw_answer!r}. "
                "Return exactly the final integer in the `answer` field."
            ),
        )

    if raw_answer == gold:
        return dspy.Prediction(
            score=1.0,
            failure_type="correct",
            parsed_answer=raw_answer,
            feedback=f"Correct. Integer answer {raw_answer} matches gold answer {gold}.",
        )

    return dspy.Prediction(
        score=0.0,
        failure_type="math",
        parsed_answer=raw_answer,
        feedback=(
            f"Math failure: integer answer {raw_answer} does not match gold answer {gold}. "
            "Review the quantities, operations, and arithmetic before changing the final answer. "
            f"Worked solution:\n{example.solution}"
        ),
    )


def metric_with_feedback(
    example: dspy.Example,
    prediction: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
) -> dspy.Prediction:
    return classify_prediction(example, prediction)


def adapter_failure_prediction(error: Exception) -> dspy.Prediction:
    return dspy.Prediction(
        score=0.0,
        failure_type="adapter",
        parsed_answer=None,
        feedback=(
            "Adapter failure: DSPy/model output could not be parsed into the structured signature. "
            f"Error: {type(error).__name__}: {error}"
        ),
    )


def evaluate(module: Any, examples: list[dspy.Example]) -> tuple[list[dict[str, Any]], float]:
    rows: list[dict[str, Any]] = []
    for ex in examples:
        error: str | None = None
        try:
            pred = module(question=ex.question)
            scored = metric_with_feedback(ex, pred)
        except Exception as exc:  # noqa: BLE001 - record model/adapter failures as data for this lab.
            pred = dspy.Prediction(reasoning=None, answer=None)
            scored = adapter_failure_prediction(exc)
            error = str(exc)

        rows.append(
            {
                "row_number": ex.row_number,
                "question": ex.question,
                "gold_answer": ex.answer,
                "pred_answer_raw": getattr(pred, "answer", None),
                "pred_answer_norm": getattr(scored, "parsed_answer", None),
                "reasoning": getattr(pred, "reasoning", None),
                "score": scored.score,
                "failure_type": scored.failure_type,
                "feedback": scored.feedback,
                "error": error,
            }
        )
    score = sum(r["score"] for r in rows) / len(rows) if rows else 0.0
    return rows, score


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("failure_type") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def summarize_instruction(module: Any) -> str:
    return repr(module)


def make_lm(*, model: str, base_url: str, temperature: float, max_tokens: int) -> dspy.LM:
    return dspy.LM(
        f"ollama_chat/{model}",
        api_base=base_url,
        api_key="",
        temperature=temperature,
        max_tokens=max_tokens,
        cache=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny reliability-first DSPy/GEPA GSM8K smoke test.")
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--train-offset", type=int, default=0)
    parser.add_argument("--train-limit", type=int, default=4)
    parser.add_argument("--val-offset", type=int, default=4)
    parser.add_argument("--val-limit", type=int, default=4)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--adapter", choices=["chat", "json"], default="chat")
    parser.add_argument("--solver-temperature", type=float, default=0.0)
    parser.add_argument("--reflection-temperature", type=float, default=0.7)
    parser.add_argument("--solver-max-tokens", type=int, default=768)
    parser.add_argument("--reflection-max-tokens", type=int, default=1024)
    parser.add_argument("--max-metric-calls", type=int, default=24)
    parser.add_argument("--skip-gepa", action="store_true", help="Only run the structured baseline reliability check.")
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()

    data_path = Path(args.data)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    solver_lm = make_lm(
        model=args.model,
        base_url=args.base_url,
        temperature=args.solver_temperature,
        max_tokens=args.solver_max_tokens,
    )
    reflection_lm = make_lm(
        model=args.model,
        base_url=args.base_url,
        temperature=args.reflection_temperature,
        max_tokens=args.reflection_max_tokens,
    )
    adapter = make_adapter(args.adapter)
    dspy.configure(lm=solver_lm, adapter=adapter)

    trainset = load_examples(data_path, offset=args.train_offset, limit=args.train_limit)
    valset = load_examples(data_path, offset=args.val_offset, limit=args.val_limit)

    baseline = GSM8KStructuredSolver()
    baseline_rows, baseline_score = evaluate(baseline, valset)

    compiled = None
    compiled_error = None
    compiled_rows: list[dict[str, Any]] = []
    compiled_score = 0.0
    if not args.skip_gepa:
        optimizer = dspy.GEPA(
            metric=metric_with_feedback,
            reflection_lm=reflection_lm,
            max_metric_calls=args.max_metric_calls,
            reflection_minibatch_size=2,
            track_stats=True,
            use_merge=False,
            num_threads=1,
            seed=0,
        )
        try:
            compiled = optimizer.compile(baseline, trainset=trainset, valset=valset)
            compiled_rows, compiled_score = evaluate(compiled, valset)
        except Exception as exc:  # noqa: BLE001 - compile stability is an experimental result here.
            compiled_error = f"{type(exc).__name__}: {exc}"

    slug = (
        f"{stamp}-gsm8k-gepa-structured-{args.adapter}"
        f"-train{args.train_offset + 1}-{args.train_offset + args.train_limit}"
        f"-val{args.val_offset + 1}-{args.val_offset + args.val_limit}"
    )
    json_path = results_dir / f"{slug}.json"
    md_path = results_dir / f"{slug}-summary.md"

    result = {
        "date": stamp,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
        "model": args.model,
        "base_url": args.base_url,
        "adapter": args.adapter,
        "data": str(data_path),
        "train_rows": [ex.row_number for ex in trainset],
        "val_rows": [ex.row_number for ex in valset],
        "solver_max_tokens": args.solver_max_tokens,
        "reflection_max_tokens": args.reflection_max_tokens,
        "max_metric_calls": args.max_metric_calls,
        "baseline_score": baseline_score,
        "compiled_score": compiled_score if compiled is not None else None,
        "compiled_error": compiled_error,
        "baseline_failure_counts": failure_counts(baseline_rows),
        "compiled_failure_counts": failure_counts(compiled_rows),
        "baseline_rows": baseline_rows,
        "compiled_rows": compiled_rows,
        "baseline_program_repr": summarize_instruction(baseline),
        "compiled_program_repr": summarize_instruction(compiled) if compiled is not None else None,
        "has_detailed_results": hasattr(compiled, "detailed_results") if compiled is not None else False,
    }
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    baseline_correct = sum(r["score"] for r in baseline_rows)
    compiled_correct = sum(r["score"] for r in compiled_rows)
    lines = [
        "# DSPy/GEPA GSM8K Structured Reliability Smoke Test",
        "",
        f"- Date: {stamp}",
        f"- DSPy version: `{result['dspy_version']}`",
        f"- Model: `{args.model}` via Ollama `{args.base_url}`",
        f"- Adapter: `{args.adapter}`",
        f"- Train rows: `{result['train_rows']}`",
        f"- Validation rows: `{result['val_rows']}`",
        f"- Solver max tokens: {args.solver_max_tokens}",
        f"- Reflection max tokens: {args.reflection_max_tokens}",
        f"- GEPA budget: max_metric_calls={args.max_metric_calls}",
        f"- Structured baseline validation score: {baseline_correct:.0f}/{len(baseline_rows)} ({baseline_score * 100:.1f}%)",
        f"- Structured baseline failure counts: `{result['baseline_failure_counts']}`",
    ]
    if compiled is not None:
        lines.extend(
            [
                f"- GEPA-compiled validation score: {compiled_correct:.0f}/{len(compiled_rows)} ({compiled_score * 100:.1f}%)",
                f"- GEPA-compiled failure counts: `{result['compiled_failure_counts']}`",
            ]
        )
    else:
        lines.append(f"- GEPA-compiled validation score: not available; compile error: `{compiled_error}`")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.",
            "",
            "Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.",
            "",
            "## Validation rows",
            "",
            "| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |",
            "|---:|---:|---|---:|---|---:|",
        ]
    )
    by_row_compiled = {r["row_number"]: r for r in compiled_rows}
    for row in baseline_rows:
        comp = by_row_compiled.get(row["row_number"], {})
        lines.append(
            "| {row} | {base} ({base_mark}) | {base_fail} | {comp} ({comp_mark}) | {comp_fail} | {gold} |".format(
                row=row["row_number"],
                base=row["pred_answer_norm"],
                base_mark="✅" if row["score"] else "❌",
                base_fail=row["failure_type"],
                comp=comp.get("pred_answer_norm"),
                comp_mark="✅" if comp.get("score") else "❌",
                comp_fail=comp.get("failure_type"),
                gold=row["gold_answer"],
            )
        )
    lines.extend(["", "## Artifact", "", f"Raw JSON: `{json_path}`"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"baseline_score={baseline_score:.3f}")
    print(f"baseline_failure_counts={result['baseline_failure_counts']}")
    if compiled is not None:
        print(f"compiled_score={compiled_score:.3f}")
        print(f"compiled_failure_counts={result['compiled_failure_counts']}")
    else:
        print(f"compiled_error={compiled_error}")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
