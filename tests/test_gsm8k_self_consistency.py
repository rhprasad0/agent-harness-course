from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path("labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py")


def load_module():
    spec = importlib.util.spec_from_file_location("gsm8k_self_consistency", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_majority_vote_uses_earliest_tied_answer_and_records_tie():
    module = load_module()
    samples = [
        {"pred_norm": "18"},
        {"pred_norm": "20"},
        {"pred_norm": "18"},
        {"pred_norm": "20"},
    ]

    vote = module.majority_vote(samples)

    assert vote["voted_answer"] == "18"
    assert vote["tie"] is True
    assert vote["parsed_sample_count"] == 4
    assert vote["parse_failure_count"] == 0


def test_majority_vote_excludes_parse_failures_unless_all_samples_fail():
    module = load_module()

    mixed_vote = module.majority_vote([
        {"pred_norm": None},
        {"pred_norm": "42"},
        {"pred_norm": "42"},
    ])
    all_failed_vote = module.majority_vote([
        {"pred_norm": None},
        {"pred_norm": None},
    ])

    assert mixed_vote["voted_answer"] == "42"
    assert mixed_vote["parsed_sample_count"] == 2
    assert mixed_vote["parse_failure_count"] == 1
    assert all_failed_vote["voted_answer"] is None
    assert all_failed_vote["parsed_sample_count"] == 0
    assert all_failed_vote["parse_failure_count"] == 2


def test_compute_votes_uses_nested_prefixes_and_scores_against_gold():
    module = load_module()
    samples = [
        {"pred_norm": "10"},
        {"pred_norm": "11"},
        {"pred_norm": "11"},
        {"pred_norm": "10"},
        {"pred_norm": "11"},
    ]

    votes = module.compute_votes(samples, [1, 3, 5], gold_norm="11")

    assert votes["1"]["voted_answer"] == "10"
    assert votes["1"]["vote_correct"] is False
    assert votes["3"]["voted_answer"] == "11"
    assert votes["3"]["vote_correct"] is True
    assert votes["5"]["voted_answer"] == "11"
    assert votes["5"]["vote_correct"] is True


def test_summarize_records_counts_rescued_broken_ties_and_prefix_costs():
    module = load_module()
    records = [
        {
            "samples": [
                {"elapsed_seconds": 1.0, "ollama_eval_count": 10},
                {"elapsed_seconds": 2.0, "ollama_eval_count": 20},
                {"elapsed_seconds": 3.0, "ollama_eval_count": 30},
            ],
            "votes": {
                "1": {"vote_correct": False, "tie": False, "parsed_sample_count": 1, "parse_failure_count": 0},
                "3": {"vote_correct": True, "tie": True, "parsed_sample_count": 3, "parse_failure_count": 0},
            },
        },
        {
            "samples": [
                {"elapsed_seconds": 1.5, "ollama_eval_count": 15},
                {"elapsed_seconds": 2.5, "ollama_eval_count": 25},
                {"elapsed_seconds": 3.5, "ollama_eval_count": 35},
            ],
            "votes": {
                "1": {"vote_correct": True, "tie": False, "parsed_sample_count": 1, "parse_failure_count": 0},
                "3": {"vote_correct": False, "tie": False, "parsed_sample_count": 0, "parse_failure_count": 2},
            },
        },
    ]

    summary = module.summarize_records(records, [1, 3])

    assert summary[1]["correct_count"] == 1
    assert summary[1]["accuracy"] == 0.5
    assert summary[3]["correct_count"] == 1
    assert summary[3]["rescued_vs_n1"] == 1
    assert summary[3]["broken_vs_n1"] == 1
    assert summary[3]["tie_count"] == 1
    assert summary[3]["all_parse_fail_vote_count"] == 1
    assert summary[3]["avg_elapsed_seconds_per_question"] == 6.75
    assert summary[3]["avg_completion_tokens_per_question"] == 67.5
