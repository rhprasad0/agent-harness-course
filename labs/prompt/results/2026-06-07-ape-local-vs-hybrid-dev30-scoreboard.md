# APE Local vs Hybrid Dev-30 Scoreboard

- Date: 2026-06-07
- Solver model: `mistral:7b-instruct-q4_K_M` via local Ollama
- Dataset: `labs/prompt/data/gsm8k/test.jsonl`
- Slice: offset 0, limit 30
- Temperature: 0.0
- Generation budget: num_predict=256
- Baseline: `baseline_reasoning_dev30`

## Results

| Prompt ID | Source | Correct | Accuracy | final marker | fallback/other | Avg sec/q | Avg prompt tok | Avg completion tok |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline_reasoning_dev30` | hand baseline | 8/30 | 26.7% | 29 | 1 | 1.47 | 116.4 | 181.6 |
| `ape_local_1_john` | local APE | 8/30 | 26.7% | 24 | 6 | 1.45 | 143.4 | 189.0 |
| `ape_local_2_jane` | local APE | 7/30 | 23.3% | 23 | 7 | 1.69 | 180.4 | 208.7 |
| `ape_local_3_david` | local APE | 8/30 | 26.7% | 25 | 5 | 1.33 | 147.4 | 161.1 |
| `ape_hybrid_units_equation_check` | hybrid APE | 7/30 | 23.3% | 11 | 19 | 1.91 | 196.4 | 238.1 |
| `ape_hybrid_quantity_checklist` | hybrid APE | 8/30 | 26.7% | 12 | 18 | 1.91 | 213.4 | 238.4 |
| `ape_hybrid_goal_given_plan` | hybrid APE | 8/30 | 26.7% | 18 | 12 | 1.59 | 211.4 | 198.7 |

## Interpretation

First-pass APE candidates did **not** beat the hand baseline on the dev/search slice. Several tied the baseline at 8/30, and two underperformed at 7/30.

The hybrid prompts were more structured but often hurt output-format compliance, producing many more fallback parses than the hand baseline. That is a useful finding: extra structure can consume budget or distract the local solver from the final-answer contract.

The local optimizer also struggled as an optimizer. Its raw generation initially followed the requested format poorly and produced generic candidate prompts, which is itself evidence that local-only APE may be weak for this setup.

## Conservative status

- Hypothesis status after first APE pass: **not supported yet** on dev rows.
- This is not a final failure of prompt optimization; it means the first candidate set did not improve the fixed dev scoreboard.
- Next useful step: inspect failures or try OPRO-style scoreboard iteration using these results as the first scoreboard.
