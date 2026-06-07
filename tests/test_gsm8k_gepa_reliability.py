from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import dspy


SCRIPT_PATH = Path("labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py")


def load_module():
    spec = importlib.util.spec_from_file_location("gsm8k_gepa_smoke", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structured_signature_declares_explicit_reasoning_and_integer_answer():
    module = load_module()

    output_fields = module.GSM8KStructuredSignature.output_fields

    assert list(output_fields) == ["reasoning", "answer"]
    assert output_fields["reasoning"].annotation is str
    assert output_fields["answer"].annotation is int


def test_metric_separates_format_failure_from_math_failure_and_success():
    module = load_module()
    example = dspy.Example(answer=72, solution="#### 72")

    format_failure = module.metric_with_feedback(example, SimpleNamespace(answer="72 clips"))
    math_failure = module.metric_with_feedback(example, SimpleNamespace(answer=96))
    success = module.metric_with_feedback(example, SimpleNamespace(answer=72))

    assert format_failure.score == 0.0
    assert format_failure.failure_type == "format"
    assert "Format failure" in format_failure.feedback

    assert math_failure.score == 0.0
    assert math_failure.failure_type == "math"
    assert "Math failure" in math_failure.feedback

    assert success.score == 1.0
    assert success.failure_type == "correct"


def test_evaluate_records_exceptions_as_adapter_failures_without_crashing():
    module = load_module()

    class BrokenModule:
        def __call__(self, *, question: str):
            raise ValueError("adapter could not parse answer")

    examples = [
        dspy.Example(row_number=1, question="q", answer=72, solution="#### 72").with_inputs("question"),
    ]

    rows, score = module.evaluate(BrokenModule(), examples)

    assert score == 0.0
    assert rows[0]["score"] == 0.0
    assert rows[0]["failure_type"] == "adapter"
    assert "adapter could not parse answer" in rows[0]["error"]


def test_adapter_factory_rejects_unknown_adapter_names():
    module = load_module()

    assert type(module.make_adapter("chat")).__name__ == "ChatAdapter"
    assert type(module.make_adapter("json")).__name__ == "JSONAdapter"

    try:
        module.make_adapter("xml")
    except ValueError as exc:
        assert "Unsupported adapter" in str(exc)
    else:
        raise AssertionError("Expected make_adapter to reject unknown adapter")
