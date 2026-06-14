# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T165325Z`
Condition: `official_judge_smoke_gpt4o_blocker_valid_json`
Dataset: `labs/context/data/longmemeval/longmemeval_oracle.json`
Model: `ollama_chat/llama3:latest`
Context policy: `marked_answer_turns`
Judge provider/model: `codex-bridge` / `gpt-4o`
Limit / offset / repeats: `1` / `0` / `1`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| marked_answer_turns | 1 | 1 | 1 | n/a | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.765 | 1.000 | n/a | 0 | 138.0 | 0.48 |

## Notes

- Headline QA accuracy is GPT-4o judge accuracy when `--judge-provider codex-bridge --judge-model gpt-4o` succeeds.
- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.
- Embedding semantic grounding is diagnostic and not an official LongMemEval score.
- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.

## Row sample

### gpt4_2655b836 repeat 1

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- GPT-4o judge correct: `None`; judge error: `codex exit 1: OpenAI Codex v0.137.0
--------
workdir: /home/ryan/projects/agent-harness-course
model: gpt-4o
provider: openai
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 019ec70d-6b8e-7770-a4e9-9ae53c162250
--------
user
I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no. In addition, do not penalize off-by-one errors for the number of days. If the question asks for the number of days/weeks/months, etc., and the model makes off-by-one errors (e.g., predicting 19 days when the answer is 18), the model's response is still correct.

Question: What was the first issue I had with my new car after its first service?

Correct Answer: GPS system not functioning correctly

Model Response: I don't know.

Is the model response correct? Answer yes or no only.
ERROR: {"type":"error","status":400,"error":{"type":"invalid_request_error","message":"The 'gpt-4o' model is not supported when using Codex with a ChatGPT account."}}
ERROR: {"type":"error","status":400,"error":{"type":"invalid_request_error","message":"The 'gpt-4o' model is not supported when using Codex with a ChatGPT account."}}`
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`
