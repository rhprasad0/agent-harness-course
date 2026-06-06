# GSM8K Ollama Self-Consistency Evaluation

- Date: 2026-06-06T174939Z
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Dataset: `labs/prompt/data/gsm8k/test.jsonl`
- Slice: first 10 `test` questions
- Temperature: 0.7
- N values: `1,3,5`
- Questions: 10
- Generation budget: max N=5 samples/question, num_predict=256
- Deterministic calibration reference: `labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval-summary.md` reported 35/100 at temperature 0 for the same first-100 slice.

| N | Correct | Accuracy | Rescued vs N=1 | Broken vs N=1 | Ties | All-parse-fail votes | Avg sec/q | Avg completion tokens/q |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 5/10 | 50.0% | 0 | 0 | 0 | 0 | 1.42 | 180.1 |
| 3 | 6/10 | 60.0% | 1 | 0 | 4 | 0 | 4.21 | 539.8 |
| 5 | 7/10 | 70.0% | 2 | 0 | 3 | 0 | 6.68 | 854.3 |

## Interpretation

Status: passed as a harness run if this file and the paired JSONL were written without generation errors.

Scope is intentionally narrow: first-100 GSM8K test slice, one local Ollama model, one prompt, one sampling temperature, and nested majority-vote prefixes. Treat small accuracy movements as provisional rather than model-general claims.

Definitions: `Rescued vs N=1` means the sampled N=1 prefix was wrong but the larger prefix vote was correct. `Broken vs N=1` means the sampled N=1 prefix was correct but the larger prefix vote was wrong. Ties are resolved by earliest tied answer in the prefix and counted explicitly.

Raw JSONL: `labs/prompt/results/2026-06-06T174939Z-gsm8k-test-first10-ollama-mistral-7b-instruct-q4_K_M-self-consistency.jsonl`
