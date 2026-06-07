# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T163847Z
- DSPy version: `3.2.1`
- Model: `llama3:latest` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `gpt-5.4` via `openai-compatible` at `http://kube1.lan:4001/v1`
- Train rows: `[5, 6, 7, 8, 9, 10, 11, 12]`
- Validation rows: `[13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]`
- Solver max tokens: 1536
- Reflection max tokens: 1536
- GEPA budget: max_metric_calls=48
- Structured baseline validation score: 10/16 (62.5%)
- Structured baseline failure counts: `{'math': 6, 'correct': 10}`
- GEPA-compiled validation score: 10/16 (62.5%)
- GEPA-compiled failure counts: `{'math': 6, 'correct': 10}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 13 | 23 (❌) | math | 12 (❌) | math | 13 |
| 14 | 18 (✅) | correct | 18 (✅) | correct | 18 |
| 15 | 60 (✅) | correct | 60 (✅) | correct | 60 |
| 16 | 2971 (❌) | math | 2971 (❌) | math | 125 |
| 17 | 230 (✅) | correct | 230 (✅) | correct | 230 |
| 18 | 59900 (❌) | math | 59900 (❌) | math | 57500 |
| 19 | 7 (✅) | correct | 7 (✅) | correct | 7 |
| 20 | 2 (❌) | math | 2 (❌) | math | 6 |
| 21 | 16 (❌) | math | 16 (❌) | math | 15 |
| 22 | 12 (❌) | math | 12 (❌) | math | 14 |
| 23 | 7 (✅) | correct | 7 (✅) | correct | 7 |
| 24 | 8 (✅) | correct | 8 (✅) | correct | 8 |
| 25 | 26 (✅) | correct | 26 (✅) | correct | 26 |
| 26 | 2 (✅) | correct | 2 (✅) | correct | 2 |
| 27 | 243 (✅) | correct | 243 (✅) | correct | 243 |
| 28 | 16 (✅) | correct | 16 (✅) | correct | 16 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T163847Z-gsm8k-gepa-structured-json-train5-12-val13-28.json`
