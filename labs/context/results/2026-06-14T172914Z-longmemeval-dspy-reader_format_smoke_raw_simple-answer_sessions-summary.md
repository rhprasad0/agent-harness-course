# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T172914Z`
Condition: `reader_format_smoke_raw_simple`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Reader / context format: `simple` / `raw`
Context policy: `answer_sessions`
Judge provider/model: `codex-bridge` / `gpt-5.4`
Limit / offset / repeats: `1` / `0` / `1`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_sessions | 1 | 1 | 1 | 0.000 | 0 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | n/a | 0 | 1881.0 | 3.58 |

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
- Pred: I don't know.
- Evidence quote:
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`
