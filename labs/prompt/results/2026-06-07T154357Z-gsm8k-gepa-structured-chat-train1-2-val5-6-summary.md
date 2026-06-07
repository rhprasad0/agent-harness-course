# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T154357Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Adapter: `chat`
- Train rows: `[1, 2]`
- Validation rows: `[5, 6]`
- Solver max tokens: 768
- Reflection max tokens: 1024
- GEPA budget: max_metric_calls=24
- Structured baseline validation score: 1/2 (50.0%)
- Structured baseline failure counts: `{'correct': 1, 'math': 1}`
- GEPA-compiled validation score: not available; compile error: `None`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 5 | 20 (✅) | correct | None (❌) | None | 20 |
| 6 | 95 (❌) | math | None (❌) | None | 64 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T154357Z-gsm8k-gepa-structured-chat-train1-2-val5-6.json`
