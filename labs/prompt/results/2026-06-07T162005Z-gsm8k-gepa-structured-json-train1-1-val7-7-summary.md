# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T162005Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `mistral:7b-instruct-q4_K_M` via `ollama` at `http://127.0.0.1:11434`
- Train rows: `[1]`
- Validation rows: `[7]`
- Solver max tokens: 1536
- Reflection max tokens: 1024
- GEPA budget: max_metric_calls=24
- Structured baseline validation score: 0/1 (0.0%)
- Structured baseline failure counts: `{'math': 1}`
- GEPA-compiled validation score: not available; compile error: `None`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 7 | 0 (❌) | math | None (❌) | None | 260 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T162005Z-gsm8k-gepa-structured-json-train1-1-val7-7.json`
