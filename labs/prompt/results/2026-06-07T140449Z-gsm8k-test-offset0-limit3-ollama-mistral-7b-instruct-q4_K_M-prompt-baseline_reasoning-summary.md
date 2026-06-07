# GSM8K Prompt Template Evaluation

- Date: 2026-06-07T140449Z
- Prompt ID: `baseline_reasoning`
- Prompt template: `labs/prompt/prompts/gsm8k_baseline_reasoning.txt`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Dataset: `labs/prompt/data/gsm8k/test.jsonl`
- Slice: offset 0, limit 3
- Temperature: 0.0
- Generation budget: num_predict=256
- Result: 2/3 correct (66.7%)
- Average elapsed: 3.29s/question
- Average prompt tokens reported by Ollama: 106.0
- Average completion tokens reported by Ollama: 202.7

## Parse statuses

| Status | Count |
|---|---:|
| `final_answer_marker` | 3 |

## Per-question results

| Row | Correct | Pred | Gold | Parse status | Question |
|---:|:---:|---:|---:|---|---|
| 1 | ✅ | 18 | 18 | `final_answer_marker` | Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every... |
| 2 | ✅ | 3 | 3 | `final_answer_marker` | A robe takes 2 bolts of blue fiber and half that much white fiber.  How many bolts in total does it take? |
| 3 | ❌ | 17 | 70000 | `final_answer_marker` | Josh decides to try flipping a house.  He buys a house for $80,000 and then puts in $50,000 in repairs.  This increas... |

## Notes

This evaluator intentionally does not generate or optimize prompts. It only scores a supplied prompt template so APE, OPRO, and GEPA candidates can be compared through the same harness.
Raw JSONL: `labs/prompt/results/2026-06-07T140449Z-gsm8k-test-offset0-limit3-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning.jsonl`
