# Frozen DSPy Reader LongMemEval Comparison — Codex gpt-5.4 Judge

Status: **non-official judged baseline, reader still frozen**

This rerun uses the LongMemEval-style yes/no judge prompt templates from `evaluate_qa.py`, routed through the Codex bridge with `--judge-model gpt-5.4`. This is **not** the official LongMemEval GPT-4o score, but it is closer to the benchmark scoring shape than the earlier local heuristic table.

The DSPy reader was not tuned for this rerun.

## Scoreboard

| Policy | Dataset role | Rows | Questions | Repeats | gpt-5.4 judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | Parse errors | Mean context words |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `marked_answer_turns` | oracle answer turns | 15 | 3 | 5 | 0.333 | 0 | 0.333 | 0.222 | 1.000 | 0.667 | 0.922 | 1.000 | 0 | 142.7 |
| `answer_sessions` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 1883.3 |
| `lexical_retrieval` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.333 | 0 | 1965.3 |
| `recent` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0 | 0.000 | 0.000 | 0.333 | 0.000 | 0.210 | 0.167 | 0 | 1928.3 |
| `all` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 1939.7 |

## What the judged rerun says

- The judged results are basically as grim as the heuristic results.
- Oracle answer turns still only pass 1 of 3 questions across five repeats.
- `answer_sessions` selects the answer sessions perfectly on this slice, but the frozen reader still gets 0/3 by the judge.
- `lexical_retrieval`, `recent`, and truncated `all` also fail end-to-end on this first-three slice.

## Interpretation

The main failure is not just retrieval. The clearest diagnostic is `answer_sessions`:

```text
recall_any@3 = 1.000
recall_all@3 = 1.000
gpt-5.4 judge acc = 0.000
```

So when the correct sessions are supplied, the frozen reader/context format still fails. Retrieval tuning before reader tuning would be cargo-culting the goblin.

## Caveats

- This is a tiny 3-question slice with five repeats.
- The judge is Codex `gpt-5.4`, not the official LongMemEval `gpt-4o-2024-08-06` evaluator.
- Longer-context policies generated DSPy/LiteLLM truncation warnings, which are part of the baseline evidence.
- No reader prompt/context-format tuning was done before this run.

## Source artifacts

- `2026-06-14T165810Z-longmemeval-dspy-gpt54_judge_marked_answer_turns_5run_slice-marked_answer_turns-summary.md`
- `2026-06-14T165926Z-longmemeval-dspy-gpt54_judge_frozen_reader_s_first3_answer_sessions-answer_sessions-summary.md`
- `2026-06-14T170047Z-longmemeval-dspy-gpt54_judge_frozen_reader_s_first3_lexical_retrieval-lexical_retrieval-summary.md`
- `2026-06-14T170255Z-longmemeval-dspy-gpt54_judge_frozen_reader_s_first3_recent-recent-summary.md`
- `2026-06-14T170537Z-longmemeval-dspy-gpt54_judge_frozen_reader_s_first3_all-all-summary.md`
