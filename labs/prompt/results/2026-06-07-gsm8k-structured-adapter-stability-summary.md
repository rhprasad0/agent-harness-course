# DSPy Structured Adapter Stability Check

- Date: 2026-06-07
- Model: `mistral:7b-instruct-q4_K_M` via local Ollama
- Harness: `scripts/run_gsm8k_gepa_dspy_smoke.py`
- Mode: structured baseline only (`--skip-gepa`)
- Train rows: `[1, 2]`
- Validation rows: `[5, 6, 7, 8]`
- Solver max tokens: `768`
- Reflection max tokens: `1024` (configured but unused because GEPA was skipped)
- Repeats: 3 per adapter

## Commands

```sh
for adapter in chat json; do
  for i in 1 2 3; do
    /tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py \
      --skip-gepa \
      --adapter "$adapter" \
      --train-limit 2 \
      --val-offset 4 \
      --val-limit 4 \
      --solver-max-tokens 768 \
      --reflection-max-tokens 1024
  done
done
```

## Aggregate result

| Adapter | Repeat scores | Total failure counts across 12 row-evals | Stability read |
|---|---:|---|---|
| `chat` | `1/4`, `0/4`, `0/4` | `{'correct': 1, 'math': 11}` | Schema/adapter stable, answers not fully deterministic |
| `json` | `0/4`, `0/4`, `0/4` | `{'math': 12}` | Schema/adapter stable, answers deterministic on this slice |

## Per-run artifacts

| Adapter | Timestamp | Score | Failure counts | Artifact |
|---|---|---:|---|---|
| `chat` | `2026-06-07T155324Z` | `1/4` | `{'correct': 1, 'math': 3}` | [`2026-06-07T155324Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md`](./2026-06-07T155324Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md) |
| `chat` | `2026-06-07T155336Z` | `0/4` | `{'math': 4}` | [`2026-06-07T155336Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md`](./2026-06-07T155336Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md) |
| `chat` | `2026-06-07T155348Z` | `0/4` | `{'math': 4}` | [`2026-06-07T155348Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md`](./2026-06-07T155348Z-gsm8k-gepa-structured-chat-train1-2-val5-8-summary.md) |
| `json` | `2026-06-07T155358Z` | `0/4` | `{'math': 4}` | [`2026-06-07T155358Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md`](./2026-06-07T155358Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md) |
| `json` | `2026-06-07T155405Z` | `0/4` | `{'math': 4}` | [`2026-06-07T155405Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md`](./2026-06-07T155405Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md) |
| `json` | `2026-06-07T155411Z` | `0/4` | `{'math': 4}` | [`2026-06-07T155411Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md`](./2026-06-07T155411Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md) |

## Row-level stability

| Adapter | Row | Observed parsed answers / failure types |
|---|---:|---|
| `chat` | 5 | `20/correct` once, `2/math` twice |
| `chat` | 6 | `95/math` three times |
| `chat` | 7 | `140/math` three times |
| `chat` | 8 | `200/math` twice, `50/math` once |
| `json` | 5 | `2/math` three times |
| `json` | 6 | `95/math` three times |
| `json` | 7 | `140/math` three times |
| `json` | 8 | `100/math` three times |

## Interpretation

- Reliability/schema finding: no `format` or `adapter` failures appeared in 24 structured row-evaluations. The redesign appears to have stabilized parse/schema handling on this slice.
- Accuracy finding: neither adapter is accurate on this small slice. Most failures are genuine `math` failures.
- Determinism finding: `json` was deterministic on this slice; `chat` was not fully deterministic even with temperature `0.0`.
- Conservative next step: prefer `json` if the next experiment is about output stability and failure-mode cleanliness; prefer `chat` only if a slightly larger check shows materially better accuracy despite some answer variance.
