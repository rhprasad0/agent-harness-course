# GSM8K Ollama Self-Consistency Evaluation

- Date: 2026-06-06T170252Z
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Dataset: `labs/prompt/data/gsm8k/test.jsonl`
- Slice: first 3 `test` questions
- Temperature: 0.7
- N values: `1,3`
- Questions: 3
- Generation budget: max N=3 samples/question, num_predict=256
- Deterministic calibration reference: `labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval-summary.md` reported 35/100 at temperature 0 for the same first-100 slice.

| N | Correct | Accuracy | Rescued vs N=1 | Broken vs N=1 | Ties | All-parse-fail votes | Avg sec/q | Avg completion tokens/q |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2/3 | 66.7% | 0 | 0 | 0 | 0 | 1.83 | 134.0 |
| 3 | 2/3 | 66.7% | 0 | 0 | 1 | 0 | 4.37 | 448.7 |

## Interpretation

Status: passed as a harness run if this file and the paired JSONL were written without generation errors.

Scope is intentionally narrow: first-100 GSM8K test slice, one local Ollama model, one prompt, one sampling temperature, and nested majority-vote prefixes. Treat small accuracy movements as provisional rather than model-general claims.

Definitions: `Rescued vs N=1` means the sampled N=1 prefix was wrong but the larger prefix vote was correct. `Broken vs N=1` means the sampled N=1 prefix was correct but the larger prefix vote was wrong. Ties are resolved by earliest tied answer in the prefix and counted explicitly.

Raw JSONL: `labs/prompt/results/2026-06-06T170252Z-gsm8k-test-first3-ollama-mistral-7b-instruct-q4_K_M-self-consistency.jsonl`
