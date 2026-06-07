#!/usr/bin/env python3
"""Evaluate one prompt template on a GSM8K slice via local Ollama.

This is the foundation for the prompt-optimization lab: optimizers can produce
candidate prompt templates, but every candidate must pass through the same boring
scoring harness before we believe anything. Tiny clipboard, big consequences.
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
DEFAULT_PROMPT_TEMPLATE = "labs/prompt/prompts/gsm8k_baseline_reasoning.txt"


def load_rows(path: Path, *, offset: int, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx < offset:
                continue
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


def parse_status(text: str, pred_raw: str | None) -> str:
    if pred_raw is None:
        return "parse_error"
    if re.search(r"FINAL_ANSWER\s*[:=]", text, flags=re.IGNORECASE):
        return "final_answer_marker"
    if re.search(r"####\s*[-+$]?[0-9]", text):
        return "gsm8k_marker"
    if re.search(r"(?:the\s+)?answer\s+is", text, flags=re.IGNORECASE):
        return "answer_is_fallback"
    return "last_number_fallback"


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


def render_prompt(template: str, question: str) -> str:
    if "{question}" in template:
        return template.format(question=question)
    return template.rstrip() + "\n\nQuestion:\n" + question + "\n"


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "prompt"


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_summary(path: Path, *, args: argparse.Namespace, stamp: str, records: list[dict[str, Any]], jsonl_path: Path) -> None:
    total = len(records)
    correct_count = sum(1 for r in records if r["correct"])
    parse_counts = Counter(r["parse_status"] for r in records)
    avg_elapsed = sum(r["elapsed_seconds"] for r in records) / total if total else 0.0
    avg_completion_tokens = sum((r.get("ollama_eval_count") or 0) for r in records) / total if total else 0.0
    avg_prompt_tokens = sum((r.get("ollama_prompt_eval_count") or 0) for r in records) / total if total else 0.0

    lines = [
        "# GSM8K Prompt Template Evaluation",
        "",
        f"- Date: {stamp}",
        f"- Prompt ID: `{args.prompt_id}`",
        f"- Prompt template: `{args.prompt_template}`",
        f"- Model: `{args.model}` via Ollama `{args.base_url}`",
        f"- Dataset: `{args.data}`",
        f"- Slice: offset {args.offset}, limit {args.limit}",
        f"- Temperature: {args.temperature}",
        f"- Generation budget: num_predict={args.num_predict}",
        f"- Result: {correct_count}/{total} correct ({(correct_count / total * 100) if total else 0:.1f}%)",
        f"- Average elapsed: {avg_elapsed:.2f}s/question",
        f"- Average prompt tokens reported by Ollama: {avg_prompt_tokens:.1f}",
        f"- Average completion tokens reported by Ollama: {avg_completion_tokens:.1f}",
        "",
        "## Parse statuses",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(parse_counts.items()):
        lines.append(f"| `{status}` | {count} |")

    lines.extend([
        "",
        "## Per-question results",
        "",
        "| Row | Correct | Pred | Gold | Parse status | Question |",
        "|---:|:---:|---:|---:|---|---|",
    ])
    for rec in records:
        q = rec["question"].replace("|", "\\|").replace("\n", " ")
        if len(q) > 120:
            q = q[:117] + "..."
        pred = rec["pred_norm"] if rec["pred_norm"] is not None else ""
        lines.append(
            f"| {rec['row_number']} | {'✅' if rec['correct'] else '❌'} | {pred} | {rec['gold_norm']} | `{rec['parse_status']}` | {q} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "This evaluator intentionally does not generate or optimize prompts. It only scores a supplied prompt template so APE, OPRO, and GEPA candidates can be compared through the same harness.",
        f"Raw JSONL: `{jsonl_path}`",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a GSM8K prompt template with local Ollama.")
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--offset", type=int, default=0, help="0-based row offset into the JSONL data file")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--prompt-template", default=DEFAULT_PROMPT_TEMPLATE)
    parser.add_argument("--prompt-id", default="baseline_reasoning")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()

    if args.offset < 0:
        parser.error("--offset must be >= 0")
    if args.limit <= 0:
        parser.error("--limit must be > 0")

    data_path = Path(args.data)
    prompt_path = Path(args.prompt_template)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    template = prompt_path.read_text(encoding="utf-8")
    rows = load_rows(data_path, offset=args.offset, limit=args.limit)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    split = data_path.stem
    slug = (
        f"{stamp}-gsm8k-{split}-offset{args.offset}-limit{args.limit}-"
        f"ollama-{slugify(args.model)}-prompt-{slugify(args.prompt_id)}"
    )
    jsonl_path = results_dir / f"{slug}.jsonl"
    md_path = results_dir / f"{slug}-summary.md"

    records: list[dict[str, Any]] = []
    for local_idx, row in enumerate(rows, start=1):
        row_number = args.offset + local_idx
        question = row["question"]
        gold_raw = gold_answer(row["answer"])
        gold_norm = normalize_numeric(gold_raw)
        prompt = render_prompt(template, question)
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
            response = {}
            text = ""
            pred_raw = None
            pred_norm = None
            correct = False
            error = repr(exc)

        status = parse_status(text, pred_raw)
        rec = {
            "row_number": row_number,
            "local_index": local_idx,
            "prompt_id": args.prompt_id,
            "prompt_template_path": str(prompt_path),
            "question": question,
            "gold_raw": gold_raw,
            "gold_norm": gold_norm,
            "pred_raw": pred_raw,
            "pred_norm": pred_norm,
            "correct": correct,
            "parse_status": status,
            "elapsed_seconds": round(elapsed, 3),
            "model_response": text,
            "ollama_eval_count": response.get("eval_count"),
            "ollama_prompt_eval_count": response.get("prompt_eval_count"),
            "ollama_total_duration_ns": response.get("total_duration"),
            "error": error,
        }
        records.append(rec)
        print(
            f"row={row_number:03d} pred={pred_norm!r} gold={gold_norm!r} "
            f"correct={correct} parse={status} elapsed={elapsed:.1f}s"
        )

    write_jsonl(jsonl_path, records)
    write_summary(md_path, args=args, stamp=stamp, records=records, jsonl_path=jsonl_path)
    print(f"\nwrote {jsonl_path}")
    print(f"wrote {md_path}")
    return 0 if all(r["error"] is None for r in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
