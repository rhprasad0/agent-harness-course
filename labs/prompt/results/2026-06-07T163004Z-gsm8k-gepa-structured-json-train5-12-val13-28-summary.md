# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T163004Z
- DSPy version: `3.2.1`
- Model: `llama2:7b-chat-q4_0` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `gpt-5.4` via `openai-compatible` at `http://kube1.lan:4001/v1`
- Train rows: `[5, 6, 7, 8, 9, 10, 11, 12]`
- Validation rows: `[13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]`
- Solver max tokens: 1536
- Reflection max tokens: 1536
- GEPA budget: max_metric_calls=48
- Structured baseline validation score: 0/16 (0.0%)
- Structured baseline failure counts: `{'adapter': 12, 'math': 4}`
- GEPA-compiled validation score: 2/16 (12.5%)
- GEPA-compiled failure counts: `{'adapter': 8, 'math': 6, 'correct': 2}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 13 | None (❌) | adapter | None (❌) | adapter | 13 |
| 14 | None (❌) | adapter | None (❌) | adapter | 18 |
| 15 | None (❌) | adapter | 6 (❌) | math | 60 |
| 16 | None (❌) | adapter | None (❌) | adapter | 125 |
| 17 | None (❌) | adapter | 70 (❌) | math | 230 |
| 18 | None (❌) | adapter | 12750 (❌) | math | 57500 |
| 19 | 84 (❌) | math | 40 (❌) | math | 7 |
| 20 | None (❌) | adapter | None (❌) | adapter | 6 |
| 21 | None (❌) | adapter | None (❌) | adapter | 15 |
| 22 | None (❌) | adapter | None (❌) | adapter | 14 |
| 23 | None (❌) | adapter | 7 (✅) | correct | 7 |
| 24 | 20 (❌) | math | 8 (✅) | correct | 8 |
| 25 | 75 (❌) | math | None (❌) | adapter | 26 |
| 26 | 0 (❌) | math | None (❌) | adapter | 2 |
| 27 | None (❌) | adapter | 233 (❌) | math | 243 |
| 28 | None (❌) | adapter | 900 (❌) | math | 16 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T163004Z-gsm8k-gepa-structured-json-train5-12-val13-28.json`
