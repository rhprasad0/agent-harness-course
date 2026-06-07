# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T154424Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Adapter: `chat`
- Train rows: `[1, 2]`
- Validation rows: `[5, 6]`
- Solver max tokens: 768
- Reflection max tokens: 1024
- GEPA budget: max_metric_calls=8
- Structured baseline validation score: 0/2 (0.0%)
- Structured baseline failure counts: `{'math': 2}`
- GEPA-compiled validation score: 0/2 (0.0%)
- GEPA-compiled failure counts: `{'math': 2}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 5 | 2 (❌) | math | 2 (❌) | math | 20 |
| 6 | 95 (❌) | math | 95 (❌) | math | 64 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6.json`
