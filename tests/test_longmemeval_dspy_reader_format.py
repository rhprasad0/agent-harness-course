from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


SCRIPT_PATH = Path("labs/context/scripts/run_longmemeval_dspy.py")


def load_module():
    spec = importlib.util.spec_from_file_location("longmemeval_dspy", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_record():
    return {
        "question_id": "q1",
        "question_type": "single-session-user",
        "question_date": "2023/05/30 (Tue) 23:40",
        "question": "What degree did I graduate with?",
        "answer": "Business Administration",
        "answer_session_ids": ["answer_1"],
        "haystack_session_ids": ["answer_1"],
        "haystack_dates": ["2023/05/29"],
        "haystack_sessions": [
            [
                {"role": "user", "content": "I graduated with a degree in Business Administration.", "has_answer": True},
                {"role": "assistant", "content": "Nice, that is useful career context."},
            ]
        ],
    }


def test_structured_context_rendering_adds_session_turn_and_task_scaffolding():
    module = load_module()

    context, selected_ids, truncated = module.build_context(
        sample_record(),
        policy="answer_sessions",
        top_k=3,
        max_context_chars=4000,
        max_turn_chars=1000,
        context_format="structured",
    )

    assert selected_ids == ["answer_1"]
    assert truncated is False
    assert "Retrieved memory sessions:" in context
    assert "=== SESSION 1 ===" in context
    assert "Session ID: answer_1" in context
    assert "Turn 1" in context
    assert "Speaker: user" in context
    assert "Question date: 2023/05/30 (Tue) 23:40" in context
    assert "Find the specific evidence" in context


def test_raw_context_format_preserves_existing_session_rendering_shape():
    module = load_module()

    context, _, _ = module.build_context(
        sample_record(),
        policy="answer_sessions",
        top_k=3,
        max_context_chars=4000,
        max_turn_chars=1000,
        context_format="raw",
    )

    assert context.startswith("SESSION answer_1 @ 2023/05/29")
    assert "USER [HAS_ANSWER]: I graduated" in context
    assert "Retrieved memory sessions:" not in context


def test_reader_factory_supports_evidence_answer_output_field():
    module = load_module()

    program = module.LongMemQA(predictor="predict", reader="evidence_answer")

    assert list(module.LongMemEvidenceAnswer.output_fields) == ["evidence_quote", "answer"]
    assert "NOT_FOUND" in (module.LongMemEvidenceAnswer.__doc__ or "")
    assert type(program.answerer).__name__ == "Predict"


def test_run_one_records_evidence_quote_when_reader_returns_it(monkeypatch):
    module = load_module()

    class FakeProgram:
        def __call__(self, *, question: str, question_date: str, context: str):
            return SimpleNamespace(
                evidence_quote="I graduated with a degree in Business Administration.",
                answer="Business Administration",
            )

    args = SimpleNamespace(
        context_policy="answer_sessions",
        top_k=3,
        max_context_chars=4000,
        max_turn_chars=1000,
        context_format="structured",
        reader="evidence_answer",
        condition="unit",
        dataset=Path("fake.json"),
        model="fake-model",
        semantic_metrics=False,
        embedding_model="",
        judge_provider="none",
        judge_model="",
    )

    row = module.run_one(args, FakeProgram(), sample_record(), repeat_index=1, run_id="run")

    assert row["raw_response"] == "Business Administration"
    assert row["evidence_quote"] == "I graduated with a degree in Business Administration."
    assert row["heuristic_correct"] is True
    assert row["context_format"] == "structured"
    assert row["reader"] == "evidence_answer"
