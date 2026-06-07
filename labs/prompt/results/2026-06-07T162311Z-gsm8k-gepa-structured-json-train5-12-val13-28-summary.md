# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T162311Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `gpt-5.4` via `openai-compatible` at `http://kube1.lan:4001/v1`
- Train rows: `[5, 6, 7, 8, 9, 10, 11, 12]`
- Validation rows: `[13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]`
- Solver max tokens: 1536
- Reflection max tokens: 1536
- GEPA budget: max_metric_calls=48
- Structured baseline validation score: 3/16 (18.8%)
- Structured baseline failure counts: `{'math': 13, 'correct': 3}`
- GEPA-compiled validation score: 3/16 (18.8%)
- GEPA-compiled failure counts: `{'math': 13, 'correct': 3}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 13 | 5 (❌) | math | 5 (❌) | math | 13 |
| 14 | 15 (❌) | math | 15 (❌) | math | 18 |
| 15 | 80 (❌) | math | 80 (❌) | math | 60 |
| 16 | 750 (❌) | math | 750 (❌) | math | 125 |
| 17 | 80 (❌) | math | 80 (❌) | math | 230 |
| 18 | 9100 (❌) | math | 9100 (❌) | math | 57500 |
| 19 | 24 (❌) | math | 24 (❌) | math | 7 |
| 20 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 21 | 10 (❌) | math | 10 (❌) | math | 15 |
| 22 | 21 (❌) | math | 21 (❌) | math | 14 |
| 23 | 12 (❌) | math | 12 (❌) | math | 7 |
| 24 | 8 (✅) | correct | 8 (✅) | correct | 8 |
| 25 | 24 (❌) | math | 24 (❌) | math | 26 |
| 26 | 2 (✅) | correct | 2 (✅) | correct | 2 |
| 27 | 252 (❌) | math | 252 (❌) | math | 243 |
| 28 | 240 (❌) | math | 240 (❌) | math | 16 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T162311Z-gsm8k-gepa-structured-json-train5-12-val13-28.json`
