#!/usr/bin/env python3
"""Run a simple DSPy QA program on a small LongMemEval slice.

The goal is Context Module 12 evidence, not leaderboard performance. The script
keeps the DSPy program intentionally small and varies the context policy around
it so the lab can isolate context construction.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import dspy
except ImportError as exc:  # pragma: no cover - environment preflight
    raise SystemExit(
        "DSPy is not installed. Try: python3 -m venv /tmp/agent-harness-dspy-venv && "
        "/tmp/agent-harness-dspy-venv/bin/python -m pip install -r labs/prompt/requirements-dspy.txt"
    ) from exc


class LongMemAnswer(dspy.Signature):
    """Answer a user-memory question using only the supplied chat-history context.

    If the answer is not supported by the supplied context, say "I don't know".
    Return a short answer, not a full explanation.
    """

    question: str = dspy.InputField(desc="The LongMemEval question to answer.")
    question_date: str = dspy.InputField(desc="Timestamp when the question is asked.")
    context: str = dspy.InputField(desc="Selected chat-history context for this policy/run.")
    answer: str = dspy.OutputField(desc="Short answer grounded only in the supplied context.")


class LongMemEvidenceAnswer(dspy.Signature):
    """Find supporting evidence first, then answer from retrieved memory context.

    If no supporting evidence exists, set evidence_quote to "NOT_FOUND" and
    answer to "I don't know". The final answer should be short and should not
    include explanation text.
    """

    question: str = dspy.InputField(desc="The LongMemEval question to answer.")
    question_date: str = dspy.InputField(desc="Timestamp when the question is asked.")
    context: str = dspy.InputField(desc="Structured retrieved chat-history context for this policy/run.")
    evidence_quote: str = dspy.OutputField(desc="Shortest quote from context that supports the answer, or NOT_FOUND.")
    answer: str = dspy.OutputField(desc="Short final answer grounded only in the supplied evidence.")


class LongMemQA(dspy.Module):
    def __init__(self, predictor: str = "predict", reader: str = "simple") -> None:
        super().__init__()
        signature = LongMemEvidenceAnswer if reader == "evidence_answer" else LongMemAnswer
        if predictor == "chain_of_thought":
            self.answerer = dspy.ChainOfThought(signature)
        else:
            self.answerer = dspy.Predict(signature)

    def forward(self, question: str, question_date: str, context: str) -> dspy.Prediction:
        return self.answerer(question=question, question_date=question_date, context=context)


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def token_f1(gold: str, pred: str) -> float:
    gold_tokens = normalize_text(gold).split()
    pred_tokens = normalize_text(pred).split()
    if not gold_tokens or not pred_tokens:
        return 0.0
    gold_counts = Counter(gold_tokens)
    pred_counts = Counter(pred_tokens)
    overlap = sum((gold_counts & pred_counts).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def heuristic_correct(gold: str, pred: str) -> bool:
    gold_norm = normalize_text(gold)
    pred_norm = normalize_text(pred)
    if not gold_norm or not pred_norm:
        return False
    if gold_norm in pred_norm:
        return True
    # Let very short model outputs count when they are an exact contained alias.
    if len(pred_norm.split()) <= 8 and pred_norm in gold_norm:
        return True
    return token_f1(gold, pred) >= 0.80


def recall_any_at_k(ranked_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return math.nan
    return 1.0 if set(ranked_ids[:k]) & set(gold_ids) else 0.0


def recall_all_at_k(ranked_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return math.nan
    return 1.0 if set(gold_ids).issubset(set(ranked_ids[:k])) else 0.0


def ndcg_any_at_k(ranked_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return math.nan
    gold = set(gold_ids)
    dcg = 0.0
    for idx, session_id in enumerate(ranked_ids[:k], start=1):
        if session_id in gold:
            dcg += 1.0 / math.log2(idx + 1)
    ideal_hits = min(len(gold), k)
    idcg = sum(1.0 / math.log2(idx + 1) for idx in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else math.nan


def mean_reciprocal_rank(ranked_ids: list[str], gold_ids: list[str]) -> float:
    gold = set(gold_ids)
    if not gold:
        return math.nan
    for idx, session_id in enumerate(ranked_ids, start=1):
        if session_id in gold:
            return 1.0 / idx
    return 0.0


def mean_numeric(rows: list[dict[str, Any]], key: str) -> float:
    vals: list[float] = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, bool):
            vals.append(1.0 if value else 0.0)
        elif isinstance(value, (int, float)) and not math.isnan(float(value)):
            vals.append(float(value))
    return sum(vals) / len(vals) if vals else math.nan


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}, got {type(data).__name__}")
    return data


def render_session(session_id: str, date: str, turns: list[dict[str, Any]], max_turn_chars: int) -> str:
    lines = [f"SESSION {session_id} @ {date}"]
    for turn in turns:
        role = str(turn.get("role", "unknown")).upper()
        content = str(turn.get("content", ""))
        if max_turn_chars and len(content) > max_turn_chars:
            content = content[: max_turn_chars - 20].rstrip() + " ... [truncated]"
        marker = " [HAS_ANSWER]" if turn.get("has_answer") is True else ""
        lines.append(f"{role}{marker}: {content}")
    return "\n".join(lines)


def render_structured_session(index: int, session_id: str, date: str, turns: list[dict[str, Any]], max_turn_chars: int) -> str:
    lines = [
        f"=== SESSION {index} ===",
        f"Session ID: {session_id}",
        f"Session date: {date}",
        "",
    ]
    for turn_index, turn in enumerate(turns, start=1):
        role = str(turn.get("role", "unknown"))
        content = str(turn.get("content", ""))
        if max_turn_chars and len(content) > max_turn_chars:
            content = content[: max_turn_chars - 20].rstrip() + " ... [truncated]"
        marker = "yes" if turn.get("has_answer") is True else "no"
        lines.extend(
            [
                f"Turn {turn_index}",
                f"Speaker: {role}",
                f"Has answer marker: {marker}",
                "Text:",
                content,
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def record_sessions(record: dict[str, Any]) -> list[tuple[str, str, list[dict[str, Any]]]]:
    ids = record.get("haystack_session_ids", [])
    dates = record.get("haystack_dates", [])
    sessions = record.get("haystack_sessions", [])
    return [(str(session_id), str(date), session) for session_id, date, session in zip(ids, dates, sessions)]


def simple_session_score(question: str, session: list[dict[str, Any]], session_id: str) -> float:
    q_terms = {t for t in normalize_text(question).split() if len(t) > 2}
    text = normalize_text(" ".join(str(turn.get("content", "")) for turn in session))
    score = sum(1 for term in q_terms if term in text)
    # Tiny deterministic tie-breaker so run order is stable.
    return score + (sum(ord(c) for c in session_id) % 997) / 1_000_000


def select_sessions(record: dict[str, Any], policy: str, top_k: int) -> list[tuple[str, str, list[dict[str, Any]]]]:
    sessions = record_sessions(record)
    if policy in {"all", "oracle"}:
        return sessions
    if policy == "recent":
        return sessions[-top_k:]
    if policy == "first":
        return sessions[:top_k]
    if policy == "answer_sessions":
        answer_ids = {str(session_id) for session_id in record.get("answer_session_ids", [])}
        selected = [triple for triple in sessions if triple[0] in answer_ids]
        return selected or sessions[:top_k]
    if policy == "lexical_retrieval":
        ranked = sorted(
            sessions,
            key=lambda triple: simple_session_score(record.get("question", ""), triple[2], triple[0]),
            reverse=True,
        )
        return ranked[:top_k]
    if policy == "marked_answer_turns":
        selected = []
        for session_id, date, session in sessions:
            turns = [turn for turn in session if turn.get("has_answer") is True]
            if turns:
                selected.append((session_id, date, turns))
        return selected or sessions[:top_k]
    raise ValueError(f"Unknown context policy: {policy}")


def build_context(
    record: dict[str, Any],
    policy: str,
    top_k: int,
    max_context_chars: int,
    max_turn_chars: int,
    context_format: str = "raw",
) -> tuple[str, list[str], bool]:
    selected = select_sessions(record, policy, top_k)
    rendered: list[str] = []
    used_ids: list[str] = []
    total = 0
    truncated = False
    for index, (session_id, date, turns) in enumerate(selected, start=1):
        if context_format == "structured":
            block = render_structured_session(index, session_id, date, turns, max_turn_chars)
        else:
            block = render_session(session_id, date, turns, max_turn_chars)
        extra = len(block) + (2 if rendered else 0)
        if max_context_chars and total + extra > max_context_chars:
            remaining = max_context_chars - total - (2 if rendered else 0)
            if remaining > 200:
                rendered.append(block[:remaining].rstrip() + "\n... [context truncated]")
                used_ids.append(session_id)
            truncated = True
            break
        rendered.append(block)
        used_ids.append(session_id)
        total += extra
    body = "\n\n".join(rendered)
    if context_format != "structured":
        return body, used_ids, truncated
    header = "\n".join(
        [
            "You are answering from retrieved memory sessions.",
            f"Question date: {record.get('question_date', '')}",
            f"Question: {record.get('question', '')}",
            "",
            "Retrieved memory sessions:",
            "",
        ]
    )
    task = "\n".join(
        [
            "",
            "Task:",
            "1. Find the specific evidence in the retrieved sessions.",
            "2. If evidence is present, answer with the shortest correct answer.",
            "3. If evidence is absent, answer exactly: I don't know.",
        ]
    )
    return header + body + task, used_ids, truncated


def get_anscheck_prompt(task: str, question: str, answer: str, response: str, abstention: bool = False) -> str:
    """LongMemEval v1 official answer-check prompt templates.

    Source: https://github.com/xiaowu0162/LongMemEval/blob/main/src/evaluation/evaluate_qa.py
    """
    if not abstention:
        if task in ["single-session-user", "single-session-assistant", "multi-session"]:
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no. \n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            return template.format(question, answer, response)
        if task == "temporal-reasoning":
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no. In addition, do not penalize off-by-one errors for the number of days. If the question asks for the number of days/weeks/months, etc., and the model makes off-by-one errors (e.g., predicting 19 days when the answer is 18), the model's response is still correct. \n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            return template.format(question, answer, response)
        if task == "knowledge-update":
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response contains some previous information along with an updated answer, the response should be considered as correct as long as the updated answer is the required answer.\n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            return template.format(question, answer, response)
        if task == "single-session-preference":
            template = "I will give you a question, a rubric for desired personalized response, and a response from a model. Please answer yes if the response satisfies the desired response. Otherwise, answer no. The model does not need to reflect all the points in the rubric. The response is correct as long as it recalls and utilizes the user's personal information correctly.\n\nQuestion: {}\n\nRubric: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            return template.format(question, answer, response)
        raise NotImplementedError(f"Unsupported LongMemEval question_type: {task}")
    template = "I will give you an unanswerable question, an explanation, and a response from a model. Please answer yes if the model correctly identifies the question as unanswerable. The model could say that the information is incomplete, or some other information is given but the asked information is not.\n\nQuestion: {}\n\nExplanation: {}\n\nModel Response: {}\n\nDoes the model correctly identify the question as unanswerable? Answer yes or no only."
    return template.format(question, answer, response)


def parse_yes_no_like_official(raw: str) -> bool:
    # The official LongMemEval script labels True with: 'yes' in eval_response.lower().
    return "yes" in raw.lower()


def judge_with_codex_bridge(args: argparse.Namespace, prompt: str) -> tuple[bool | None, str, str]:
    """Return (label, raw_response, error) using Codex CLI as a GPT bridge."""
    command = [
        "codex",
        "exec",
        "--model",
        args.judge_model,
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--ignore-rules",
        "--output-last-message",
    ]
    try:
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
            tmp_path = tmp.name
        command.extend([tmp_path, "-"])
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=args.judge_timeout_sec,
            check=False,
        )
        raw = ""
        try:
            raw = Path(tmp_path).read_text(encoding="utf-8").strip()
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        if completed.returncode != 0:
            stderr = completed.stderr.strip()[-2000:]
            stdout = completed.stdout.strip()[-1000:]
            return None, raw, f"codex exit {completed.returncode}: {stderr or stdout}"
        if not raw:
            raw = completed.stdout.strip()
        return parse_yes_no_like_official(raw), raw, ""
    except Exception as exc:  # noqa: BLE001 - judge failures are row-level evidence
        return None, "", f"{type(exc).__name__}: {exc}"


def judge_row(args: argparse.Namespace, row: dict[str, Any]) -> dict[str, Any]:
    if args.judge_provider == "none":
        return {
            "judge_correct": None,
            "judge_model": "",
            "judge_provider": "none",
            "judge_raw_response": "",
            "judge_error": "",
        }
    if args.judge_provider != "codex-bridge":
        return {
            "judge_correct": None,
            "judge_model": args.judge_model,
            "judge_provider": args.judge_provider,
            "judge_raw_response": "",
            "judge_error": f"unsupported judge provider: {args.judge_provider}",
        }
    try:
        prompt = get_anscheck_prompt(
            str(row.get("question_type", "")),
            str(row.get("question", "")),
            str(row.get("gold_answer", "")),
            str(row.get("raw_response", "")),
            abstention="_abs" in str(row.get("question_id", "")),
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "judge_correct": None,
            "judge_model": args.judge_model,
            "judge_provider": args.judge_provider,
            "judge_raw_response": "",
            "judge_error": f"prompt error: {type(exc).__name__}: {exc}",
        }
    label, raw, error = judge_with_codex_bridge(args, prompt)
    return {
        "judge_correct": label,
        "judge_model": args.judge_model,
        "judge_provider": args.judge_provider,
        "judge_raw_response": raw,
        "judge_error": error,
    }


def ollama_embedding(text: str, model: str, api_base: str) -> list[float]:
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        api_base.rstrip("/") + "/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [float(x) for x in data["embedding"]]


def cosine(a: list[float], b: list[float]) -> float:
    denom = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    if denom == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / denom


def chunk_text(text: str, chunk_chars: int, max_chunks: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text) and len(chunks) < max_chunks:
        chunks.append(text[start : start + chunk_chars])
        start += chunk_chars
    return chunks


def semantic_grounding_metrics(args: argparse.Namespace, gold: str, pred: str, context: str) -> dict[str, float | str]:
    empty = {
        "answer_semantic_similarity": math.nan,
        "gold_context_similarity": math.nan,
        "pred_context_similarity": math.nan,
        "semantic_grounding_index": math.nan,
        "semantic_metric_error": "",
    }
    if not args.semantic_metrics:
        return empty
    if not args.embedding_model:
        return {**empty, "semantic_metric_error": "semantic metrics requested without --embedding-model"}
    if not pred.strip() or not gold.strip():
        return {
            "answer_semantic_similarity": 0.0,
            "gold_context_similarity": 0.0,
            "pred_context_similarity": 0.0,
            "semantic_grounding_index": 0.0,
            "semantic_metric_error": "",
        }
    try:
        gold_emb = ollama_embedding(gold, args.embedding_model, args.embedding_api_base)
        pred_emb = ollama_embedding(pred, args.embedding_model, args.embedding_api_base)
        chunks = chunk_text(context, args.embedding_chunk_chars, args.embedding_max_context_chunks)
        chunk_embs = [ollama_embedding(chunk, args.embedding_model, args.embedding_api_base) for chunk in chunks if chunk.strip()]
        answer_sim = cosine(pred_emb, gold_emb)
        gold_context = max((cosine(gold_emb, emb) for emb in chunk_embs), default=0.0)
        pred_context = max((cosine(pred_emb, emb) for emb in chunk_embs), default=0.0)
        return {
            "answer_semantic_similarity": answer_sim,
            "gold_context_similarity": gold_context,
            "pred_context_similarity": pred_context,
            "semantic_grounding_index": answer_sim * gold_context * pred_context,
            "semantic_metric_error": "",
        }
    except Exception as exc:  # noqa: BLE001 - row-level diagnostic failures are evidence
        return {
            "answer_semantic_similarity": math.nan,
            "gold_context_similarity": math.nan,
            "pred_context_similarity": math.nan,
            "semantic_grounding_index": math.nan,
            "semantic_metric_error": f"{type(exc).__name__}: {exc}",
        }


def retrieval_metrics(selected_ids: list[str], answer_ids: list[str]) -> dict[str, float]:
    return {
        "recall_any@1": recall_any_at_k(selected_ids, answer_ids, 1),
        "recall_any@3": recall_any_at_k(selected_ids, answer_ids, 3),
        "recall_any@5": recall_any_at_k(selected_ids, answer_ids, 5),
        "recall_all@3": recall_all_at_k(selected_ids, answer_ids, 3),
        "recall_all@5": recall_all_at_k(selected_ids, answer_ids, 5),
        "ndcg_any@3": ndcg_any_at_k(selected_ids, answer_ids, 3),
        "ndcg_any@5": ndcg_any_at_k(selected_ids, answer_ids, 5),
        "mrr": mean_reciprocal_rank(selected_ids, answer_ids),
    }


def run_one(args: argparse.Namespace, program: LongMemQA, record: dict[str, Any], repeat_index: int, run_id: str) -> dict[str, Any]:
    context, selected_ids, context_truncated = build_context(
        record,
        policy=args.context_policy,
        top_k=args.top_k,
        max_context_chars=args.max_context_chars,
        max_turn_chars=args.max_turn_chars,
        context_format=args.context_format,
    )
    gold = str(record.get("answer", ""))
    answer_ids = [str(session_id) for session_id in record.get("answer_session_ids", [])]
    base = {
        "run_id": run_id,
        "condition": args.condition,
        "dataset": str(args.dataset),
        "model": args.model,
        "reader": getattr(args, "reader", "simple"),
        "context_format": args.context_format,
        "context_policy": args.context_policy,
        "repeat_index": repeat_index,
        "question_id": record.get("question_id"),
        "question_type": record.get("question_type"),
        "question_date": record.get("question_date"),
        "question": record.get("question"),
        "gold_answer": gold,
        "selected_session_ids": selected_ids,
        "answer_session_ids": answer_ids,
        "selected_session_count": len(selected_ids),
        "total_haystack_sessions": len(record.get("haystack_sessions", [])),
        "context_chars": len(context),
        "context_words": len(context.split()),
        "context_truncated": context_truncated,
        "evidence_session_hit": bool(set(selected_ids) & set(answer_ids)),
        **retrieval_metrics(selected_ids, answer_ids),
    }
    started = time.perf_counter()
    try:
        pred = program(
            question=str(record.get("question", "")),
            question_date=str(record.get("question_date", "")),
            context=context,
        )
        elapsed = time.perf_counter() - started
        answer = str(pred.answer).strip()
        evidence_quote = str(getattr(pred, "evidence_quote", "")).strip()
        row = {
            **base,
            "raw_response": answer,
            "evidence_quote": evidence_quote,
            "parse_error": "",
            "elapsed_sec": elapsed,
            "heuristic_correct": heuristic_correct(gold, answer),
            "token_f1": token_f1(gold, answer),
        }
    except Exception as exc:  # noqa: BLE001 - row-level failures are evidence
        elapsed = time.perf_counter() - started
        row = {
            **base,
            "raw_response": "",
            "evidence_quote": "",
            "parse_error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": elapsed,
            "heuristic_correct": False,
            "token_f1": 0.0,
        }
    row.update(semantic_grounding_metrics(args, gold, str(row.get("raw_response", "")), context))
    row.update(judge_row(args, row))
    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"rows": 0}
    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_policy[str(row["context_policy"])].append(row)

    policy_summary = {}
    for policy, group in by_policy.items():
        heuristic_scores = [1.0 if row["heuristic_correct"] else 0.0 for row in group]
        judged = [row for row in group if row.get("judge_correct") is not None]
        judge_scores = [1.0 if row.get("judge_correct") else 0.0 for row in judged]
        policy_summary[policy] = {
            "rows": len(group),
            "heuristic_accuracy": sum(heuristic_scores) / len(heuristic_scores),
            "heuristic_accuracy_stdev": statistics.pstdev(heuristic_scores) if len(heuristic_scores) > 1 else 0.0,
            "judge_accuracy": sum(judge_scores) / len(judge_scores) if judge_scores else math.nan,
            "judge_accuracy_stdev": statistics.pstdev(judge_scores) if len(judge_scores) > 1 else 0.0,
            "judged_rows": len(judged),
            "judge_errors": sum(1 for row in group if row.get("judge_error")),
            "mean_token_f1": mean_numeric(group, "token_f1"),
            "evidence_hit_rate": mean_numeric(group, "evidence_session_hit"),
            "mean_recall_any@3": mean_numeric(group, "recall_any@3"),
            "mean_recall_all@3": mean_numeric(group, "recall_all@3"),
            "mean_ndcg_any@3": mean_numeric(group, "ndcg_any@3"),
            "mean_mrr": mean_numeric(group, "mrr"),
            "mean_answer_semantic_similarity": mean_numeric(group, "answer_semantic_similarity"),
            "mean_gold_context_similarity": mean_numeric(group, "gold_context_similarity"),
            "mean_pred_context_similarity": mean_numeric(group, "pred_context_similarity"),
            "mean_semantic_grounding_index": mean_numeric(group, "semantic_grounding_index"),
            "semantic_metric_errors": sum(1 for row in group if row.get("semantic_metric_error")),
            "parse_errors": sum(1 for row in group if row["parse_error"]),
            "mean_context_words": mean_numeric(group, "context_words"),
            "mean_elapsed_sec": mean_numeric(group, "elapsed_sec"),
        }

    return {
        "rows": len(rows),
        "question_ids": len({row["question_id"] for row in rows}),
        "repeats": len({row["repeat_index"] for row in rows}),
        "policies": policy_summary,
    }


def json_sanitize(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: json_sanitize(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [json_sanitize(inner) for inner in value]
    return value


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(json_sanitize(row), sort_keys=True) + "\n")


def hypothesis_payload(row: dict[str, Any], include_metadata: bool = False) -> dict[str, Any]:
    payload = {
        "question_id": row["question_id"],
        "hypothesis": row["raw_response"],
    }
    if include_metadata:
        payload.update(
            {
                "repeat_index": row["repeat_index"],
                "context_policy": row["context_policy"],
                "condition": row["condition"],
            }
        )
    return payload


def write_hypotheses_all_repeats(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(hypothesis_payload(row, include_metadata=True), sort_keys=True) + "\n")


def write_hypotheses_by_repeat(out_dir: Path, stem: str, rows: list[dict[str, Any]]) -> list[Path]:
    paths = []
    repeats = sorted({int(row["repeat_index"]) for row in rows})
    for repeat in repeats:
        repeat_rows = [row for row in rows if int(row["repeat_index"]) == repeat]
        path = out_dir / f"{stem}-repeat{repeat}-hypotheses.jsonl"
        with path.open("w") as f:
            for row in repeat_rows:
                f.write(json.dumps(hypothesis_payload(row), sort_keys=True) + "\n")
        paths.append(path)
    return paths


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "run_id",
        "condition",
        "model",
        "reader",
        "context_format",
        "context_policy",
        "repeat_index",
        "question_id",
        "question_type",
        "judge_correct",
        "judge_model",
        "judge_provider",
        "judge_error",
        "heuristic_correct",
        "token_f1",
        "evidence_session_hit",
        "recall_any@1",
        "recall_any@3",
        "recall_any@5",
        "recall_all@3",
        "recall_all@5",
        "ndcg_any@3",
        "ndcg_any@5",
        "mrr",
        "answer_semantic_similarity",
        "gold_context_similarity",
        "pred_context_similarity",
        "semantic_grounding_index",
        "semantic_metric_error",
        "selected_session_count",
        "total_haystack_sessions",
        "context_words",
        "context_chars",
        "context_truncated",
        "elapsed_sec",
        "parse_error",
        "question",
        "gold_answer",
        "raw_response",
        "evidence_quote",
        "judge_raw_response",
        "selected_session_ids",
        "answer_session_ids",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def fmt_float(value: Any, digits: int = 3) -> str:
    if not isinstance(value, (int, float)) or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    return f"{float(value):.{digits}f}"


def write_markdown(path: Path, args: argparse.Namespace, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# LongMemEval DSPy Run Summary",
        "",
        f"Run ID: `{rows[0]['run_id'] if rows else 'n/a'}`",
        f"Condition: `{args.condition}`",
        f"Dataset: `{args.dataset}`",
        f"Model: `{args.model}`",
        f"Reader / context format: `{args.reader}` / `{args.context_format}`",
        f"Context policy: `{args.context_policy}`",
        f"Judge provider/model: `{args.judge_provider}` / `{args.judge_model if args.judge_provider != 'none' else 'n/a'}`",
        f"Limit / offset / repeats: `{args.limit}` / `{args.offset}` / `{args.repeats}`",
        "",
        "## Aggregate",
        "",
        "| Policy | Rows | Questions | Repeats | Judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for policy, stats in summary.get("policies", {}).items():
        lines.append(
            f"| {policy} | {stats['rows']} | {summary.get('question_ids', 0)} | {summary.get('repeats', 0)} | "
            f"{fmt_float(stats['judge_accuracy'])} | {stats['judge_errors']} | {fmt_float(stats['heuristic_accuracy'])} | "
            f"{fmt_float(stats['mean_token_f1'])} | {fmt_float(stats['mean_recall_any@3'])} | "
            f"{fmt_float(stats['mean_recall_all@3'])} | {fmt_float(stats['mean_ndcg_any@3'])} | "
            f"{fmt_float(stats['mean_mrr'])} | {fmt_float(stats['mean_semantic_grounding_index'])} | "
            f"{stats['parse_errors']} | {fmt_float(stats['mean_context_words'], 1)} | {fmt_float(stats['mean_elapsed_sec'], 2)} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Headline QA accuracy is judge accuracy from the configured judge provider/model; official LongMemEval comparison still requires GPT-4o.",
            "- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.",
            "- Embedding semantic grounding is diagnostic and not an official LongMemEval score.",
            "- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.",
            "- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.",
            "",
            "## Row sample",
            "",
        ]
    )
    for row in rows[: min(5, len(rows))]:
        lines.extend(
            [
                f"### {row['question_id']} repeat {row['repeat_index']}",
                "",
                f"- Type: `{row['question_type']}`",
                f"- Question: {row['question']}",
                f"- Gold: {row['gold_answer']}",
                f"- Pred: {row['raw_response']}",
                f"- Evidence quote: {row.get('evidence_quote', '')}",
                f"- Judge correct: `{row.get('judge_correct')}`; judge error: `{row.get('judge_error', '')}`",
                f"- Heuristic correct: `{row['heuristic_correct']}`; F1: `{row['token_f1']:.3f}`; evidence hit: `{row['evidence_session_hit']}`",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("labs/context/data/longmemeval/longmemeval_oracle.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("labs/context/results"))
    parser.add_argument("--condition", default="longmemeval_dspy_simple")
    parser.add_argument("--model", default="ollama_chat/llama3:latest")
    parser.add_argument("--api-base", default="http://localhost:11434")
    parser.add_argument("--adapter", choices=["chat", "json"], default="chat")
    parser.add_argument("--predictor", choices=["predict", "chain_of_thought"], default="predict")
    parser.add_argument("--reader", choices=["simple", "evidence_answer"], default="simple")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument(
        "--context-policy",
        choices=["oracle", "all", "recent", "first", "answer_sessions", "lexical_retrieval", "marked_answer_turns"],
        default="oracle",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--max-context-chars", type=int, default=24000)
    parser.add_argument("--max-turn-chars", type=int, default=2000)
    parser.add_argument("--context-format", choices=["raw", "structured"], default="raw")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--question-type", default="")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--judge-provider", choices=["none", "codex-bridge"], default="none")
    parser.add_argument("--judge-model", default="gpt-4o")
    parser.add_argument("--judge-timeout-sec", type=int, default=120)
    parser.add_argument("--semantic-metrics", action="store_true")
    parser.add_argument("--embedding-model", default="")
    parser.add_argument("--embedding-api-base", default="http://localhost:11434")
    parser.add_argument("--embedding-max-context-chunks", type=int, default=8)
    parser.add_argument("--embedding-chunk-chars", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.dataset)
    if args.question_type:
        records = [row for row in records if row.get("question_type") == args.question_type]
    if args.offset:
        records = records[args.offset :]
    if args.limit:
        records = records[: args.limit]

    lm = dspy.LM(args.model, api_base=args.api_base, temperature=args.temperature, max_tokens=args.max_tokens, cache=False)
    adapter = dspy.ChatAdapter() if args.adapter == "chat" else dspy.JSONAdapter()
    dspy.configure(lm=lm, adapter=adapter)
    program = LongMemQA(predictor=args.predictor, reader=args.reader)

    run_id = utc_run_id()
    rows: list[dict[str, Any]] = []
    for repeat_index in range(1, args.repeats + 1):
        for record in records:
            row = run_one(args, program, record, repeat_index, run_id)
            rows.append(row)
            status = "OK" if row["heuristic_correct"] else "MISS"
            if row["parse_error"]:
                status = "ERR"
            judge_status = ""
            if args.judge_provider != "none":
                if row.get("judge_error"):
                    judge_status = " judge=ERR"
                else:
                    judge_status = f" judge={row.get('judge_correct')}"
            print(
                f"{row['question_id']} repeat={repeat_index} {status} "
                f"f1={row['token_f1']:.3f} words={row['context_words']} elapsed={row['elapsed_sec']:.2f}s{judge_status}"
            )

    summary = summarize(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{run_id}-longmemeval-dspy-{args.condition}-{args.context_policy}"
    jsonl_path = args.out_dir / f"{stem}.jsonl"
    csv_path = args.out_dir / f"{stem}-summary.csv"
    md_path = args.out_dir / f"{stem}-summary.md"
    metrics_path = args.out_dir / f"{stem}-metrics.json"
    hyp_all_path = args.out_dir / f"{stem}-hypotheses-all-repeats.jsonl"
    judge_results_path = args.out_dir / f"{stem}-judge-results.jsonl"
    write_jsonl(jsonl_path, rows)
    write_csv(csv_path, rows)
    write_markdown(md_path, args, rows, summary)
    metrics_path.write_text(json.dumps(json_sanitize(summary), indent=2, sort_keys=True) + "\n")
    write_hypotheses_all_repeats(hyp_all_path, rows)
    repeat_hyp_paths = write_hypotheses_by_repeat(args.out_dir, stem, rows)
    write_jsonl(
        judge_results_path,
        [
            {
                "question_id": row.get("question_id"),
                "repeat_index": row.get("repeat_index"),
                "context_policy": row.get("context_policy"),
                "judge_correct": row.get("judge_correct"),
                "judge_model": row.get("judge_model"),
                "judge_provider": row.get("judge_provider"),
                "judge_raw_response": row.get("judge_raw_response"),
                "judge_error": row.get("judge_error"),
            }
            for row in rows
        ],
    )
    print(f"wrote {jsonl_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print(f"wrote {metrics_path}")
    print(f"wrote {hyp_all_path}")
    for path in repeat_hyp_paths:
        print(f"wrote {path}")
    print(f"wrote {judge_results_path}")
    print(json.dumps(json_sanitize(summary), indent=2, sort_keys=True))

    if args.judge_provider != "none" and all(row.get("judge_error") for row in rows):
        raise SystemExit("official judge scoring blocked: every row has judge_error")


if __name__ == "__main__":
    main()
