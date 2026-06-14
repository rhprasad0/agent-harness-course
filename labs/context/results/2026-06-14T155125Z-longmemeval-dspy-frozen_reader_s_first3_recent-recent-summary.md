# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T155125Z`
Condition: `frozen_reader_s_first3_recent`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Context policy: `recent`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | Accuracy | Accuracy stdev | Mean F1 | Evidence hit | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recent | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0.333 | 0 | 1928.3 | 5.61 |

## Notes

- Scoring is a lightweight local heuristic: normalized substring match or token F1 >= 0.80.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.
- Treat this as a harness smoke / small-slice lab artifact, not a LongMemEval leaderboard result.

## Row sample

### e47becba repeat 1

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### 118b2229 repeat 1

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I don't know. The context doesn't provide enough information about the specific question asked.
- Correct: `False`; F1: `0.000`; evidence hit: `False`

### 51a45a95 repeat 1

- Type: `single-session-user`
- Question: Where did I redeem a $5 coupon on coffee creamer?
- Gold: Target
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `False`

### e47becba repeat 2

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### 118b2229 repeat 2

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I don't know. The context doesn't provide enough information about the specific question asked.
- Correct: `False`; F1: `0.000`; evidence hit: `False`
