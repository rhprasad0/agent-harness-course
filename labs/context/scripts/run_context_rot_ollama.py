#!/usr/bin/env python3
"""Run a small context-rot / lost-in-the-middle probe against Ollama.

This harness intentionally uses only the Python standard library so the lab remains
portable and easy to inspect. It varies approximate context size and needle
position while keeping the model, question, hidden fact, and scoring rule fixed.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED_ANSWER = "mango-orbit-92"
QUESTION = "What is the Project Lantern access code?"
NEEDLE = f"Project Lantern access code is {EXPECTED_ANSWER}."
OLLAMA_URL = "http://localhost:11434/api/generate"

FILLER_SUBJECTS = [
    "The archive clerk",
    "A field observer",
    "The planning memo",
    "A maintenance note",
    "The logistics record",
    "A training vignette",
    "The status digest",
    "A neutral briefing",
    "The shift report",
    "A project diary",
]
FILLER_VERBS = [
    "describes",
    "summarizes",
    "records",
    "mentions",
    "outlines",
    "reviews",
    "compares",
    "indexes",
    "tracks",
    "notes",
]
FILLER_OBJECTS = [
    "routine weather observations near a quiet storage yard",
    "inventory labels for ordinary boxes of office supplies",
    "meeting times for a fictional committee on paper forms",
    "maintenance steps for a harmless training simulator",
    "parking assignments for a temporary classroom exercise",
    "color-coded folders used in a sample documentation drill",
    "lunch preferences gathered during a mock scheduling exercise",
    "fictional map references from a classroom navigation problem",
    "benign checklist items for a practice operations binder",
    "public-domain trivia used as placeholder text in a lesson",
]
FILLER_ENDINGS = [
    "without assigning any password or secret value.",
    "and avoids access credentials entirely.",
    "while keeping all identifiers synthetic and harmless.",
    "with no security-sensitive material included.",
    "as plain filler for a context-window experiment.",
    "so the paragraph remains irrelevant to the question.",
]


def parse_csv_ints(value: str) -> list[int]:
    try:
        parsed = [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not parsed or any(item <= 0 for item in parsed):
        raise argparse.ArgumentTypeError("expected comma-separated positive integers")
    return parsed


def parse_csv_strings(value: str) -> list[str]:
    parsed = [part.strip() for part in value.split(",") if part.strip()]
    allowed = {"beginning", "middle", "end"}
    invalid = sorted(set(parsed) - allowed)
    if invalid:
        raise argparse.ArgumentTypeError(f"invalid positions: {', '.join(invalid)}")
    if not parsed:
        raise argparse.ArgumentTypeError("expected at least one position")
    return parsed


def utc_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def words(text: str) -> list[str]:
    return text.split()


def build_filler_units(seed: int, count: int) -> list[str]:
    rng = random.Random(seed)
    units: list[str] = []
    for index in range(count):
        sentence = " ".join(
            [
                rng.choice(FILLER_SUBJECTS),
                rng.choice(FILLER_VERBS),
                rng.choice(FILLER_OBJECTS),
                rng.choice(FILLER_ENDINGS),
            ]
        )
        units.append(f"Record {index + 1:04d}. {sentence}")
    return units


def estimate_units_for_target(target_context_tokens: int) -> int:
    # The harness avoids tokenizer dependencies. These filler units are usually
    # around 20-25 words, so this intentionally underfills a little to leave room
    # for prompt overhead inside Llama 2's 4096-token native window.
    return max(1, round(target_context_tokens / 24))


def assemble_context(target_context_tokens: int, position: str, seed: int) -> tuple[str, int, int, int]:
    unit_count = estimate_units_for_target(target_context_tokens)
    filler = build_filler_units(seed=seed, count=unit_count)

    if position == "beginning":
        needle_index = 0
    elif position == "middle":
        needle_index = len(filler) // 2
    elif position == "end":
        needle_index = len(filler)
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(f"unknown position {position!r}")

    parts = list(filler)
    parts.insert(needle_index, NEEDLE)
    context = "\n".join(parts)
    prefix = "\n".join(parts[:needle_index])
    needle_offset_words = len(words(prefix))
    return context, unit_count, needle_index, needle_offset_words


def build_prompt(context: str) -> str:
    return f"""You are given a context document and a question.
Answer the question using only the context document.
Return only the exact access code. Do not explain.

Context document:
---
{context}
---

Question: {QUESTION}
Answer:
"""


def normalize_answer(text: str) -> str:
    normalized = text.strip().lower()
    normalized = normalized.strip('`"\'“”‘’.:;，。')
    # If the model returns a sentence, keep the scoring strict but recover the
    # target token for classification.
    return " ".join(normalized.split())


def classify_response(raw_response: str, normalized_response: str) -> tuple[bool, str]:
    if normalized_response == EXPECTED_ANSWER:
        return True, "correct"
    if not normalized_response:
        return False, "missing_answer"
    if EXPECTED_ANSWER in normalized_response:
        return False, "extra_text"
    if "mango" in normalized_response or "orbit" in normalized_response or "92" in normalized_response:
        return False, "wrong_fact"
    return False, "format_error"


def call_ollama(
    *,
    model: str,
    prompt: str,
    temperature: float,
    num_predict: int,
    num_ctx: int,
    timeout: float,
) -> tuple[dict[str, Any] | None, str | None, float]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            elapsed = time.perf_counter() - start
            data = json.loads(response.read().decode("utf-8"))
            return data, None, elapsed
    except TimeoutError:
        return None, "timeout", time.perf_counter() - start
    except urllib.error.URLError as exc:
        return None, f"ollama_error: {exc}", time.perf_counter() - start
    except json.JSONDecodeError as exc:
        return None, f"ollama_error: invalid JSON response: {exc}", time.perf_counter() - start


def length_label(target_context_tokens: int) -> str:
    if target_context_tokens <= 512:
        return "short"
    if target_context_tokens <= 1536:
        return "medium"
    return "long"


def run_trial(args: argparse.Namespace, run_id: str, target_context_tokens: int, position: str, repeat: int) -> dict[str, Any]:
    seed = args.seed + (target_context_tokens * 17) + (repeat * 101) + {"beginning": 1, "middle": 2, "end": 3}[position]
    context, unit_count, needle_index, needle_offset_words = assemble_context(target_context_tokens, position, seed)
    prompt = build_prompt(context)
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    trial_id = f"{length_label(target_context_tokens)}-{position}-{repeat:03d}"

    base_row: dict[str, Any] = {
        "run_id": run_id,
        "model": args.model,
        "trial_id": trial_id,
        "length_label": length_label(target_context_tokens),
        "target_context_tokens": target_context_tokens,
        "position": position,
        "repeat": repeat,
        "seed": seed,
        "filler_unit_count": unit_count,
        "needle_offset_units": needle_index,
        "needle_offset_words": needle_offset_words,
        "context_words": len(words(context)),
        "prompt_chars": len(prompt),
        "prompt_sha256": prompt_sha256,
        "question": QUESTION,
        "expected_answer": EXPECTED_ANSWER,
        "num_ctx": args.num_ctx,
        "num_predict": args.num_predict,
        "temperature": args.temperature,
    }

    if args.dry_run:
        return {
            **base_row,
            "raw_response": "",
            "normalized_response": "",
            "correct": False,
            "failure_type": "dry_run",
            "elapsed_seconds": 0.0,
            "prompt_eval_count": None,
            "eval_count": None,
            "response_chars": 0,
            "ollama_done_reason": None,
            "error": None,
        }

    data, error, elapsed = call_ollama(
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        num_predict=args.num_predict,
        num_ctx=args.num_ctx,
        timeout=args.timeout,
    )
    if error:
        failure_type = "timeout" if error == "timeout" else "ollama_error"
        return {
            **base_row,
            "raw_response": "",
            "normalized_response": "",
            "correct": False,
            "failure_type": failure_type,
            "elapsed_seconds": round(elapsed, 3),
            "prompt_eval_count": None,
            "eval_count": None,
            "response_chars": 0,
            "ollama_done_reason": None,
            "error": error,
        }

    assert data is not None
    raw_response = str(data.get("response", ""))
    normalized = normalize_answer(raw_response)
    correct, failure_type = classify_response(raw_response, normalized)
    return {
        **base_row,
        "raw_response": raw_response,
        "normalized_response": normalized,
        "correct": correct,
        "failure_type": failure_type,
        "elapsed_seconds": round(elapsed, 3),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
        "response_chars": len(raw_response),
        "ollama_done_reason": data.get("done_reason"),
        "error": None,
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["target_context_tokens"]), str(row["position"]))].append(row)

    summary: list[dict[str, Any]] = []
    for (target_context_tokens, position), group in sorted(grouped.items()):
        correct_count = sum(1 for row in group if row["correct"])
        prompt_counts = [row["prompt_eval_count"] for row in group if isinstance(row.get("prompt_eval_count"), int)]
        elapsed = [float(row["elapsed_seconds"]) for row in group]
        failures = Counter(str(row["failure_type"]) for row in group)
        summary.append(
            {
                "target_context_tokens": target_context_tokens,
                "length_label": length_label(target_context_tokens),
                "position": position,
                "trials": len(group),
                "correct": correct_count,
                "accuracy": correct_count / len(group) if group else 0.0,
                "avg_prompt_eval_count": round(statistics.mean(prompt_counts), 1) if prompt_counts else "",
                "avg_elapsed_seconds": round(statistics.mean(elapsed), 3) if elapsed else "",
                "failure_counts": "; ".join(f"{key}={value}" for key, value in sorted(failures.items())),
            }
        )
    return summary


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_summary_csv(path: Path, summary: list[dict[str, Any]]) -> None:
    fieldnames = [
        "target_context_tokens",
        "length_label",
        "position",
        "trials",
        "correct",
        "accuracy",
        "avg_prompt_eval_count",
        "avg_elapsed_seconds",
        "failure_counts",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)


def write_summary_md(path: Path, args: argparse.Namespace, run_id: str, summary: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    correct = sum(1 for row in rows if row["correct"])
    failures = Counter(str(row["failure_type"]) for row in rows)
    lines = [
        f"# Context Rot Llama2 Summary — {run_id}",
        "",
        "## Run configuration",
        "",
        f"- Model: `{args.model}`",
        f"- `num_ctx`: `{args.num_ctx}`",
        f"- `num_predict`: `{args.num_predict}`",
        f"- Temperature: `{args.temperature}`",
        f"- Target context tokens: `{','.join(str(item) for item in args.target_tokens)}`",
        f"- Positions: `{','.join(args.positions)}`",
        f"- Repeats per cell: `{args.repeats}`",
        f"- Expected answer: `{EXPECTED_ANSWER}`",
        "",
        "## Overall result",
        "",
        f"- Correct: {correct}/{total}",
        "- Failure counts: " + ", ".join(f"{key}={value}" for key, value in sorted(failures.items())),
        "",
        "## Accuracy by target length and position",
        "",
        "| Target context tokens | Observed avg prompt eval tokens | Position | Correct / Trials | Accuracy | Avg seconds | Failure counts |",
        "|---:|---:|---|---:|---:|---:|---|",
    ]
    for item in summary:
        lines.append(
            "| {target_context_tokens} | {avg_prompt_eval_count} | {position} | {correct}/{trials} | {accuracy:.3f} | {avg_elapsed_seconds} | {failure_counts} |".format(
                **item
            )
        )

    examples = [row for row in rows if not row["correct"]][:5]
    if examples:
        lines.extend(["", "## First failure examples", ""])
        for row in examples:
            raw = str(row["raw_response"]).replace("\n", "\\n")
            if len(raw) > 240:
                raw = raw[:237] + "..."
            lines.extend(
                [
                    f"- `{row['trial_id']}` ({row['failure_type']}): `{raw}`",
                ]
            )
    else:
        lines.extend(["", "## Failure examples", "", "No failures in this run."])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="llama2:7b-chat-q4_0")
    parser.add_argument("--target-tokens", type=parse_csv_ints, default=[512, 1536, 3072])
    parser.add_argument("--positions", type=parse_csv_strings, default=["beginning", "middle", "end"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-predict", type=int, default=64)
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--seed", type=int, default=12062026)
    parser.add_argument("--out-dir", type=Path, default=Path("labs/context/results"))
    parser.add_argument("--dry-run", action="store_true", help="Generate rows without calling Ollama.")
    args = parser.parse_args(argv)
    if args.repeats <= 0:
        parser.error("--repeats must be positive")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    run_id = utc_run_id()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for target_context_tokens in args.target_tokens:
        for position in args.positions:
            for repeat in range(1, args.repeats + 1):
                row = run_trial(args, run_id, target_context_tokens, position, repeat)
                rows.append(row)
                status = "OK" if row["correct"] else row["failure_type"]
                print(
                    f"{row['trial_id']}: {status} "
                    f"prompt_eval_count={row.get('prompt_eval_count')} "
                    f"elapsed={row['elapsed_seconds']}s",
                    flush=True,
                )

    stem = f"{run_id}-context-rot-llama2"
    jsonl_path = args.out_dir / f"{stem}.jsonl"
    csv_path = args.out_dir / f"{stem}-summary.csv"
    md_path = args.out_dir / f"{stem}-summary.md"

    summary = summarize(rows)
    write_jsonl(jsonl_path, rows)
    write_summary_csv(csv_path, summary)
    write_summary_md(md_path, args, run_id, summary, rows)

    total = len(rows)
    correct = sum(1 for row in rows if row["correct"])
    print(f"wrote {jsonl_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print(f"overall correct: {correct}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
