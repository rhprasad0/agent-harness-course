# DSPy/GEPA GSM8K Smoke Test

- Date: 2026-06-07T150719Z
- DSPy version: `3.2.1`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Train rows: `[1, 2, 3, 4]`
- Validation rows: `[5, 6, 7, 8]`
- GEPA budget: max_metric_calls=24
- Baseline validation score: 1/4 (25.0%)
- GEPA-compiled validation score: 1/4 (25.0%)

## Interpretation

This is a setup/learning smoke test, not a final prompt-optimization result. It verifies that DSPy can call local Ollama and that `dspy.GEPA` can run with a metric returning `dspy.Prediction(score, feedback)`.

In this tiny run, GEPA did not improve validation accuracy. That is not surprising: the budget and split are intentionally tiny, and the same local Mistral model is used as both solver and reflection model.

## Validation rows

| Row | Baseline | GEPA compiled | Gold |
|---:|---:|---:|---:|
| 5 | 20 (✅) | 20 (✅) | 20 |
| 6 | 8 (❌) | 8 (❌) | 64 |
| 7 | the final numeric answer is (❌) | the final numeric answer is (❌) | 260 |
| 8 | 120 (❌) | 120 (❌) | 160 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8.json`
