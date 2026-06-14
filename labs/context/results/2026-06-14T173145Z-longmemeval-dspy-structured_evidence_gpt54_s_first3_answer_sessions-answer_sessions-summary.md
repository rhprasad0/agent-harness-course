# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T173145Z`
Condition: `structured_evidence_gpt54_s_first3_answer_sessions`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Reader / context format: `evidence_answer` / `structured`
Context policy: `answer_sessions`
Judge provider/model: `codex-bridge` / `gpt-5.4`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_sessions | 15 | 3 | 5 | 0.333 | 0 | 0.333 | 0.222 | 1.000 | 1.000 | 1.000 | 1.000 | n/a | 0 | 1981.7 | 1.07 |

## Notes

- Headline QA accuracy is GPT-4o judge accuracy when `--judge-provider codex-bridge --judge-model gpt-4o` succeeds.
- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.
- Embedding semantic grounding is diagnostic and not an official LongMemEval score.
- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.

## Row sample

### e47becba repeat 1

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: Degree in Business Administration
- Evidence quote: I graduated with a degree in Business Administration, which has definitely helped me in my new role.
- GPT-4o judge correct: `True`; judge error: ``
- Heuristic correct: `True`; F1: `0.667`; evidence hit: `True`

### 118b2229 repeat 1

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I don't know.
- Evidence quote: You've been using the Audible app to listen to your audiobooks, and it allows you to bookmark and add notes.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### 51a45a95 repeat 1

- Type: `single-session-user`
- Question: Where did I redeem a $5 coupon on coffee creamer?
- Gold: Target
- Pred: I redeemed a $5 coupon on coffee creamer.
- Evidence quote: I actually redeemed a $5 coupon on coffee creamer last Sunday, which was a nice surprise since I didn't know I had it in my email inbox.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### e47becba repeat 2

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: Degree in Business Administration
- Evidence quote: I graduated with a degree in Business Administration, which has definitely helped me in my new role.
- GPT-4o judge correct: `True`; judge error: ``
- Heuristic correct: `True`; F1: `0.667`; evidence hit: `True`

### 118b2229 repeat 2

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I don't know.
- Evidence quote: You are already reading Gone Girl on your Kindle, but The Nightingale sounds interesting. Can you tell me more about it?
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`
