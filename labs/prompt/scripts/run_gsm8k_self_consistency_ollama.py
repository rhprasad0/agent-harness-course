#!/usr/bin/env python3
"""Run a minimal GSM8K self-consistency harness against local Ollama.

The harness samples multiple reasoning traces per question, scores nested
majority-vote prefixes, and writes public-safe JSONL + Markdown artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "mistral:7b-instruct-q4_K_M"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_DATA = "labs/prompt/data/gsm8k/test.jsonl"
DEFAULT_RESULTS_DIR = "labs/prompt/results"


def load_rows(path: Path, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if len(rows) >= limit:
                break
            rows.append(json.loads(line))
    return rows


def gold_answer(answer: str) -> str:
    if "####" not in answer:
        raise ValueError("GSM8K answer is missing final-answer marker '####'")
    return answer.split("####", 1)[1].strip()


def normalize_numeric(text: str | None) -> str | None:
    if text is None:
        return None
    s = text.strip().replace(",", "").replace("$", "")
    s = re.sub(r"\s+", "", s)
    if not s:
        return None
    try:
        d = Decimal(s)
    except InvalidOperation:
        return s.lower()
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def extract_model_answer(text: str) -> str | None:
    marker_patterns = [
        r"FINAL_ANSWER\s*[:=]\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
        r"####\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
        r"(?:the\s+)?answer\s+is\s*[:=]?\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
    ]
    for pat in marker_patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            return matches[-1]
    matches = re.findall(r"[-+$]?[0-9][0-9,]*(?:\.[0-9]+)?", text)
    return matches[-1] if matches else None


def ollama_generate(base_url: str, model: str, prompt: str, temperature: float, num_predict: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_prompt(question: str) -> str:
    return f"""Solve the following grade-school math word problem. Show your reasoning briefly, then end with exactly one line in this format:
FINAL_ANSWER: <number>

Question:
{question}
"""


def parse_n_values(text: str) -> list[int]:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise ValueError("--n-values must contain at least one positive integer")
    if any(n <= 0 for n in values):
        raise ValueError("--n-values must be positive integers")
    return sorted(set(values))


def majority_vote(samples: list[dict[str, Any]]) -> dict[str, Any]:
    parsed: list[str] = [s["pred_norm"] for s in samples if s.get("pred_norm") is not None]
    parse_failure_count = len(samples) - len(parsed)
    if not parsed:
        return {
            "voted_answer": None,
            "tie": False,
            "parsed_sample_count": 0,
            "parse_failure_count": parse_failure_count,
        }

    counts = Counter(parsed)
    top_count = max(counts.values())
    tied_answers = {answer for answer, count in counts.items() if count == top_count}
    voted_answer = next(answer for answer in parsed if answer in tied_answers)
    return {
        "voted_answer": voted_answer,
        "tie": len(tied_answers) > 1,
        "parsed_sample_count": len(parsed),
        "parse_failure_count": parse_failure_count,
    }


def compute_votes(samples: list[dict[str, Any]], n_values: list[int], gold_norm: str | None) -> dict[str, dict[str, Any]]:
    votes: dict[str, dict[str, Any]] = {}
    for n in n_values:
        vote = majority_vote(samples[:n])
        vote["vote_correct"] = vote["voted_answer"] == gold_norm
        votes[str(n)] = vote
    return votes


def summarize_records(records: list[dict[str, Any]], n_values: list[int]) -> dict[int, dict[str, Any]]:
    total = len(records)
    summary: dict[int, dict[str, Any]] = {}
    for n in n_values:
        n_key = str(n)
        correct_count = sum(1 for r in records if r["votes"][n_key]["vote_correct"])
        n1_key = "1"
        rescued = sum(
            1
            for r in records
            if not r["votes"][n1_key]["vote_correct"] and r["votes"][n_key]["vote_correct"]
        )
        broken = sum(
            1
            for r in records
            if r["votes"][n1_key]["vote_correct"] and not r["votes"][n_key]["vote_correct"]
        )
        tie_count = sum(1 for r in records if r["votes"][n_key]["tie"])
        all_parse_fail_vote_count = sum(
            1 for r in records if r["votes"][n_key]["parsed_sample_count"] == 0
        )
        elapsed_total = sum(
            sum((s.get("elapsed_seconds") or 0.0) for s in r["samples"][:n]) for r in records
        )
        token_total = sum(
            sum((s.get("ollama_eval_count") or 0) for s in r["samples"][:n]) for r in records
        )
        summary[n] = {
            "correct_count": correct_count,
            "accuracy": correct_count / total if total else 0.0,
            "rescued_vs_n1": rescued,
            "broken_vs_n1": broken,
            "tie_count": tie_count,
            "all_parse_fail_vote_count": all_parse_fail_vote_count,
            "avg_elapsed_seconds_per_question": elapsed_total / total if total else 0.0,
            "avg_completion_tokens_per_question": token_total / total if total else 0.0,
        }
    return summary


def model_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", model).strip("-")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_summary(
    path: Path,
    *,
    stamp: str,
    args: argparse.Namespace,
    data_path: Path,
    split: str,
    n_values: list[int],
    records: list[dict[str, Any]],
    jsonl_path: Path,
) -> None:
    summary = summarize_records(records, n_values)
    total = len(records)
    lines = [
        "# GSM8K Ollama Self-Consistency Evaluation",
        "",
        f"- Date: {stamp}",
        f"- Model: `{args.model}` via Ollama `{args.base_url}`",
        f"- Dataset: `{data_path}`",
        f"- Slice: first {args.limit} `{split}` questions",
        f"- Temperature: {args.temperature}",
        f"- N values: `{','.join(str(n) for n in n_values)}`",
        f"- Questions: {total}",
        f"- Generation budget: max N={max(n_values)} samples/question, num_predict={args.num_predict}",
        "- Deterministic calibration reference: `labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval-summary.md` reported 35/100 at temperature 0 for the same first-100 slice.",
        "",
        "| N | Correct | Accuracy | Rescued vs N=1 | Broken vs N=1 | Ties | All-parse-fail votes | Avg sec/q | Avg completion tokens/q |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for n in n_values:
        row = summary[n]
        lines.append(
            f"| {n} | {row['correct_count']}/{total} | {row['accuracy'] * 100:.1f}% | "
            f"{row['rescued_vs_n1']} | {row['broken_vs_n1']} | {row['tie_count']} | "
            f"{row['all_parse_fail_vote_count']} | {row['avg_elapsed_seconds_per_question']:.2f} | "
            f"{row['avg_completion_tokens_per_question']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Status: passed as a harness run if this file and the paired JSONL were written without generation errors.",
            "",
            "Scope is intentionally narrow: first-100 GSM8K test slice, one local Ollama model, one prompt, one sampling temperature, and nested majority-vote prefixes. Treat small accuracy movements as provisional rather than model-general claims.",
            "",
            "Definitions: `Rescued vs N=1` means the sampled N=1 prefix was wrong but the larger prefix vote was correct. `Broken vs N=1` means the sampled N=1 prefix was correct but the larger prefix vote was wrong. Ties are resolved by earliest tied answer in the prefix and counted explicitly.",
            "",
            f"Raw JSONL: `{jsonl_path}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_question(
    *,
    index: int,
    row: dict[str, str],
    args: argparse.Namespace,
    n_values: list[int],
) -> dict[str, Any]:
    question = row["question"]
    gold_raw = gold_answer(row["answer"])
    gold_norm = normalize_numeric(gold_raw)
    prompt = build_prompt(question)
    samples: list[dict[str, Any]] = []
    max_n = max(n_values)

    for sample_index in range(1, max_n + 1):
        start = time.time()
        try:
            response = ollama_generate(args.base_url, args.model, prompt, args.temperature, args.num_predict)
            elapsed = time.time() - start
            text = response.get("response", "")
            pred_raw = extract_model_answer(text)
            pred_norm = normalize_numeric(pred_raw)
            error = None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            elapsed = time.time() - start
            response = {}
            text = ""
            pred_raw = None
            pred_norm = None
            error = repr(exc)

        sample = {
            "sample_index": sample_index,
            "pred_raw": pred_raw,
            "pred_norm": pred_norm,
            "sample_correct": pred_norm == gold_norm,
            "elapsed_seconds": round(elapsed, 3),
            "ollama_eval_count": response.get("eval_count"),
            "ollama_prompt_eval_count": response.get("prompt_eval_count"),
            "ollama_total_duration_ns": response.get("total_duration"),
            "error": error,
            "model_response": text,
        }
        samples.append(sample)
        print(
            f"{index:03d}.{sample_index:02d}: pred={pred_norm!r} gold={gold_norm!r} "
            f"correct={sample['sample_correct']} elapsed={elapsed:.1f}s"
        )

    votes = compute_votes(samples, n_values, gold_norm)
    return {
        "index": index,
        "question": question,
        "gold_raw": gold_raw,
        "gold_norm": gold_norm,
        "model": args.model,
        "temperature": args.temperature,
        "n_values": n_values,
        "samples": samples,
        "votes": votes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--n-values", default="1,5,10,20")
    parser.add_argument("--num-predict", type=int, default=512)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--seed", default=None, help="Recorded as metadata only; sample order is not randomized in v0.")
    args = parser.parse_args()

    n_values = parse_n_values(args.n_values)
    data_path = Path(args.data)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    rows = load_rows(data_path, args.limit)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    split = data_path.stem
    slug = f"{stamp}-gsm8k-{split}-first{args.limit}-ollama-{model_slug(args.model)}-self-consistency"
    jsonl_path = results_dir / f"{slug}.jsonl"
    md_path = results_dir / f"{slug}-summary.md"

    records = [run_question(index=idx, row=row, args=args, n_values=n_values) for idx, row in enumerate(rows, start=1)]
    for record in records:
        record["seed"] = args.seed

    write_jsonl(jsonl_path, records)
    write_summary(
        md_path,
        stamp=stamp,
        args=args,
        data_path=data_path,
        split=split,
        n_values=n_values,
        records=records,
        jsonl_path=jsonl_path,
    )
    print(f"\nwrote {jsonl_path}")
    print(f"wrote {md_path}")
    had_errors = any(sample["error"] is not None for record in records for sample in record["samples"])
    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
