# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T165034Z`
Condition: `official_judge_smoke_gpt55_bridge`
Dataset: `labs/context/data/longmemeval/longmemeval_oracle.json`
Model: `ollama_chat/llama3:latest`
Context policy: `marked_answer_turns`
Judge provider/model: `codex-bridge` / `gpt-5.5`
Limit / offset / repeats: `1` / `0` / `1`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| marked_answer_turns | 1 | 1 | 1 | 0.000 | 0 | 0.000 | 0.000 | 1.000 | 0.000 | 0.765 | 1.000 | n/a | 0 | 138.0 | 0.49 |

## Notes

- Headline QA accuracy is GPT-4o judge accuracy when `--judge-provider codex-bridge --judge-model gpt-4o` succeeds.
- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.
- Embedding semantic grounding is diagnostic and not an official LongMemEval score.
- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.

## Row sample

### gpt4_2655b836 repeat 1

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`
