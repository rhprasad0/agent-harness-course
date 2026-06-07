# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T160316Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `gpt-5.4` via `openai-compatible` at `http://kube1.lan:4001/v1`
- Train rows: `[1, 2]`
- Validation rows: `[5, 6, 7, 8]`
- Solver max tokens: 1536
- Reflection max tokens: 1536
- GEPA budget: max_metric_calls=8
- Structured baseline validation score: 0/4 (0.0%)
- Structured baseline failure counts: `{'math': 3, 'adapter': 1}`
- GEPA-compiled validation score: 0/4 (0.0%)
- GEPA-compiled failure counts: `{'math': 3, 'adapter': 1}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 5 | 2 (❌) | math | 2 (❌) | math | 20 |
| 6 | 95 (❌) | math | 95 (❌) | math | 64 |
| 7 | None (❌) | adapter | None (❌) | adapter | 260 |
| 8 | 100 (❌) | math | 100 (❌) | math | 160 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T160316Z-gsm8k-gepa-structured-json-train1-2-val5-8.json`
