# Frozen DSPy Reader LongMemEval Comparison

Status: **baseline/frozen-reader evidence, not tuned**

This scoreboard intentionally freezes the simple DSPy reader from `run_longmemeval_dspy.py` and compares context policies without reader tuning. `marked_answer_turns` uses `longmemeval_oracle.json`; the other policies use the first three records from `longmemeval_s_cleaned.json`. Because those are not the same question IDs, treat `marked_answer_turns` as a separate oracle-turn reader diagnostic, not a direct baseline on the same rows.

## Aggregate

| Policy | Dataset role | Rows | Questions | Repeats | Accuracy | Accuracy stdev | Mean F1 | Evidence hit | Parse errors | Mean context words | Mean elapsed sec |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `marked_answer_turns` | oracle answer turns | 15 | 3 | 5 | 0.333 | 0.471 | 0.222 | 1.000 | 0 | 142.7 | 0.42 |
| `answer_sessions` | s_cleaned first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 1883.3 | 1.93 |
| `lexical_retrieval` | s_cleaned first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0.333 | 0 | 1965.3 | 3.02 |
| `recent` | s_cleaned first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0.333 | 0 | 1928.3 | 5.61 |
| `all` | s_cleaned first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 1939.7 | 4.25 |

## Interpretation

- The frozen reader is weak: every policy on the first three `longmemeval_s_cleaned.json` rows scored `0/3` across five repeats.
- `answer_sessions` had evidence hit `1.0` and still scored `0.0`, so the reader/context format is a bottleneck before retrieval quality.
- `lexical_retrieval` and `recent` each hit evidence on only one of three questions; `all` with the current truncation budget hit none of the answer sessions on this slice.
- The many DSPy truncation warnings during longer-context runs are part of the baseline evidence: this simple reader is not yet robust under LongMemEval context shapes.

## Source artifacts

- `2026-06-14T153321Z-longmemeval-dspy-marked_answer_turns_5run_slice-marked_answer_turns.jsonl`
- `2026-06-14T153321Z-longmemeval-dspy-marked_answer_turns_5run_slice-marked_answer_turns-summary.md`
- `2026-06-14T155000Z-longmemeval-dspy-frozen_reader_s_first3_answer_sessions-answer_sessions.jsonl`
- `2026-06-14T155000Z-longmemeval-dspy-frozen_reader_s_first3_answer_sessions-answer_sessions-summary.md`
- `2026-06-14T155035Z-longmemeval-dspy-frozen_reader_s_first3_lexical_retrieval-lexical_retrieval.jsonl`
- `2026-06-14T155035Z-longmemeval-dspy-frozen_reader_s_first3_lexical_retrieval-lexical_retrieval-summary.md`
- `2026-06-14T155125Z-longmemeval-dspy-frozen_reader_s_first3_recent-recent.jsonl`
- `2026-06-14T155125Z-longmemeval-dspy-frozen_reader_s_first3_recent-recent-summary.md`
- `2026-06-14T155254Z-longmemeval-dspy-frozen_reader_s_first3_all-all.jsonl`
- `2026-06-14T155254Z-longmemeval-dspy-frozen_reader_s_first3_all-all-summary.md`
