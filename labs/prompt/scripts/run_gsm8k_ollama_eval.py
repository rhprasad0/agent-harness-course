#!/usr/bin/env python3
"""Smoke test Ollama gpt-oss on the first N GSM8K training questions.

This is intentionally lightweight: it calls the local Ollama HTTP API, asks for a
final numeric answer marker, parses the marker, and writes JSONL + Markdown
summary artifacts under labs/prompt/results/.
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

DEFAULT_MODEL = "gpt-oss:20b"
DEFAULT_BASE_URL = "http://127.0.0.1:11434"


def load_rows(path: Path, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if len(rows) >= limit:
                break
            rows.append(json.loads(line))
    return rows


def gold_answer(answer: str) -> str:
    return answer.split("####", 1)[1].strip()


def normalize_numeric(text: str | None) -> str | None:
    if text is None:
        return None
    s = text.strip()
    s = s.replace(",", "")
    s = s.replace("$", "")
    s = re.sub(r"\s+", "", s)
    if not s:
        return None
    # Keep simple rational-looking numeric forms out of scope for now; GSM8K final
    # answers are mostly integers/decimals. If a model emits "72 clips", caller
    # should extract the number before normalizing.
    try:
        d = Decimal(s)
    except InvalidOperation:
        return s.lower()
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def extract_model_answer(text: str) -> str | None:
    # Preferred marker requested in prompt.
    marker_patterns = [
        r"FINAL_ANSWER\s*[:=]\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
        r"####\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
        r"(?:the\s+)?answer\s+is\s*[:=]?\s*([-+$]?[0-9][0-9,]*(?:\.[0-9]+)?)",
    ]
    for pat in marker_patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            return matches[-1]
    # Fallback: last number in response.
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="labs/prompt/data/gsm8k/train.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-predict", type=int, default=512)
    parser.add_argument("--results-dir", default="labs/prompt/results")
    args = parser.parse_args()

    data_path = Path(args.data)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    split = data_path.stem
    model_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", args.model).strip("-")
    slug = f"{stamp}-gsm8k-{split}-first{args.limit}-ollama-{model_slug}-eval"
    jsonl_path = results_dir / f"{slug}.jsonl"
    md_path = results_dir / f"{slug}-summary.md"

    rows = load_rows(data_path, args.limit)
    records: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        question = row["question"]
        gold_raw = gold_answer(row["answer"])
        gold_norm = normalize_numeric(gold_raw)
        prompt = build_prompt(question)
        start = time.time()
        try:
            response = ollama_generate(args.base_url, args.model, prompt, args.temperature, args.num_predict)
            elapsed = time.time() - start
            text = response.get("response", "")
            pred_raw = extract_model_answer(text)
            pred_norm = normalize_numeric(pred_raw)
            correct = pred_norm == gold_norm
            error = None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            elapsed = time.time() - start
            text = ""
            pred_raw = None
            pred_norm = None
            correct = False
            error = repr(exc)
            response = {}

        rec = {
            "index": idx,
            "question": question,
            "gold_raw": gold_raw,
            "gold_norm": gold_norm,
            "pred_raw": pred_raw,
            "pred_norm": pred_norm,
            "correct": correct,
            "elapsed_seconds": round(elapsed, 3),
            "model_response": text,
            "ollama_eval_count": response.get("eval_count"),
            "ollama_prompt_eval_count": response.get("prompt_eval_count"),
            "ollama_total_duration_ns": response.get("total_duration"),
            "error": error,
        }
        records.append(rec)
        print(f"{idx:02d}: pred={pred_norm!r} gold={gold_norm!r} correct={correct} elapsed={elapsed:.1f}s")

    with jsonl_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    counts = Counter("correct" if r["correct"] else "wrong" for r in records)
    total = len(records)
    correct_count = counts["correct"]
    avg_elapsed = sum(r["elapsed_seconds"] for r in records) / total if total else 0.0
    avg_completion_tokens = sum((r.get("ollama_eval_count") or 0) for r in records) / total if total else 0.0

    lines = [
        "# GSM8K Ollama Evaluation",
        "",
        f"- Date: {stamp}",
        f"- Model: `{args.model}` via Ollama `{args.base_url}`",
        f"- Dataset: `{data_path}`",
        f"- Slice: first {args.limit} `{split}` questions",
        f"- Temperature: {args.temperature}",
        f"- Result: {correct_count}/{total} correct ({(correct_count / total * 100) if total else 0:.1f}%)",
        f"- Average elapsed: {avg_elapsed:.2f}s/question",
        f"- Average completion tokens reported by Ollama: {avg_completion_tokens:.1f}",
        "",
        "| # | Correct | Pred | Gold | Question |",
        "|---:|:---:|---:|---:|---|",
    ]
    for rec in records:
        q = rec["question"].replace("|", "\\|").replace("\n", " ")
        if len(q) > 120:
            q = q[:117] + "..."
        lines.append(
            f"| {rec['index']} | {'✅' if rec['correct'] else '❌'} | {rec['pred_norm']} | {rec['gold_norm']} | {q} |"
        )
    lines.extend([
        "",
        "## Notes",
        "",
        "This is a deterministic 100-question calibration eval: no self-consistency yet, no few-shot exemplars, and no full-dataset claim. Tiny sample, tiny trumpet.",
        f"Raw JSONL: `{jsonl_path}`",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {jsonl_path}")
    print(f"wrote {md_path}")
    return 0 if all(r["error"] is None for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
