# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T172944Z`
Condition: `reader_format_smoke_structured_evidence`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Reader / context format: `evidence_answer` / `structured`
Context policy: `answer_sessions`
Judge provider/model: `codex-bridge` / `gpt-5.4`
Limit / offset / repeats: `1` / `0` / `1`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_sessions | 1 | 1 | 1 | 1.000 | 0 | 1.000 | 0.667 | 1.000 | 1.000 | 1.000 | 1.000 | n/a | 0 | 1939.0 | 1.79 |

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
