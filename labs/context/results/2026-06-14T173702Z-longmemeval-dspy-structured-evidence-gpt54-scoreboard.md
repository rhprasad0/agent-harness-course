# Structured Evidence Reader LongMemEval Comparison — Codex gpt-5.4 Judge

Status: **reader/context-format intervention, non-official judged baseline**

This rerun keeps the same first-three LongMemEval slice and uses the LongMemEval-style yes/no judge prompt through Codex `gpt-5.4`. It is **not** official LongMemEval GPT-4o scoring.

Change under test:

- `--context-format structured`: adds explicit question/date header, session separators, turn numbers, speaker labels, and task instructions.
- `--reader evidence_answer`: asks DSPy for an `evidence_quote` before the final short `answer`.

The retrieval/context policies are still varied around that reader. The earlier frozen-reader `gpt-5.4` scoreboard is the comparison baseline.

## Scoreboard

| Policy | Dataset role | Rows | Questions | Repeats | structured evidence gpt-5.4 acc | prior frozen gpt-5.4 acc | Δ | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | Mean context words |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `marked_answer_turns` | oracle answer turns | 15 | 3 | 5 | 0.333 | 0.333 | +0.000 | 0 | 0.333 | 0.333 | 1.000 | 0.667 | 0.922 | 1.000 | 231.7 |
| `answer_sessions` | `s_cleaned` first3 | 15 | 3 | 5 | 0.333 | 0.000 | +0.333 | 0 | 0.333 | 0.222 | 1.000 | 1.000 | 1.000 | 1.000 | 1981.7 |
| `lexical_retrieval` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | +0.000 | 0 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.333 | 2032.7 |
| `recent` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | +0.000 | 0 | 0.000 | 0.000 | 0.333 | 0.333 | 0.210 | 0.167 | 1997.7 |
| `all` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | +0.000 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2006.3 |

## Interpretation

The intervention helped exactly where the prior diagnostic said it should: `answer_sessions`.

```text
answer_sessions prior frozen reader:     0.000 judge accuracy
answer_sessions structured evidence:     0.333 judge accuracy
retrieval remained perfect:              recall_any@3 = 1.000, recall_all@3 = 1.000
```

That means the reader/context-format change rescued one of the three development questions when the correct sessions were already selected. The goblin moved, but did not surrender.

## What did not improve

- Oracle answer turns stayed at 1/3.
- Retrieval-weak policies (`lexical_retrieval`, `recent`, `all`) stayed at 0/3.
- Longer context policies still showed truncation warnings in the run output.

## Conservative claim

Supported:

> On the first-three LongMemEval development slice, adding structured context plus an evidence-first DSPy reader improved the `answer_sessions` diagnostic from 0/3 to 1/3 under a non-official Codex `gpt-5.4` LongMemEval-style judge.

Not supported yet:

> Structured memory beats stuffing the whole context.

Next:

- Inspect the two remaining `answer_sessions` failures.
- Tune context budget/rendering or evidence extraction on the dev slice only.
- Freeze the improved reader.
- Validate on a fresh held-out slice, e.g. `--offset 3 --limit 7`.

## Source artifacts

- `2026-06-14T173021Z-longmemeval-dspy-structured_evidence_gpt54_marked_answer_turns_5run_slice-marked_answer_turns-summary.md`
- `2026-06-14T173145Z-longmemeval-dspy-structured_evidence_gpt54_s_first3_answer_sessions-answer_sessions-summary.md`
- `2026-06-14T173312Z-longmemeval-dspy-structured_evidence_gpt54_s_first3_lexical_retrieval-lexical_retrieval-summary.md`
- `2026-06-14T173450Z-longmemeval-dspy-structured_evidence_gpt54_s_first3_recent-recent-summary.md`
- `2026-06-14T173702Z-longmemeval-dspy-structured_evidence_gpt54_s_first3_all-all-summary.md`
