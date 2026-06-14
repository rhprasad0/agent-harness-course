# LongMemEval Official GPT-4o Judge Attempt — Blocked

Status: **blocked before full frozen-reader rerun**

The harness was updated to support LongMemEval-style judge scoring, but the requested GPT-4o judge path through the Codex bridge is unavailable in this environment.

## What was implemented

- Official-compatible per-repeat hypothesis export.
- LongMemEval v1 answer-check prompt templates from `evaluate_qa.py`.
- `--judge-provider codex-bridge` / `--judge-model ...` row-level judge scoring.
- Row-level judge fields:
  - `judge_correct`
  - `judge_model`
  - `judge_provider`
  - `judge_raw_response`
  - `judge_error`
- Retrieval diagnostics:
  - `recall_any@1`, `recall_any@3`, `recall_any@5`
  - `recall_all@3`, `recall_all@5`
  - `ndcg_any@3`, `ndcg_any@5`
  - `mrr`
- Optional embedding semantic-grounding diagnostics.

## GPT-4o blocker

A one-row official-judge smoke was run with:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/context/scripts/run_longmemeval_dspy.py \
  --dataset labs/context/data/longmemeval/longmemeval_oracle.json \
  --condition official_judge_smoke_gpt4o_blocker \
  --context-policy marked_answer_turns \
  --limit 1 \
  --repeats 1 \
  --model ollama_chat/llama3:latest \
  --api-base http://localhost:11434 \
  --adapter chat \
  --predictor predict \
  --temperature 0 \
  --max-tokens 512 \
  --max-context-chars 12000 \
  --max-turn-chars 4000 \
  --judge-provider codex-bridge \
  --judge-model gpt-4o
```

Result:

```text
official judge scoring blocked: every row has judge_error
```

The row-level judge error says:

```text
The 'gpt-4o' model is not supported when using Codex with a ChatGPT account.
```

The blocker was reproduced with valid JSON/JSONL artifacts:

- `2026-06-14T165325Z-longmemeval-dspy-official_judge_smoke_gpt4o_blocker_valid_json-marked_answer_turns.jsonl`
- `2026-06-14T165325Z-longmemeval-dspy-official_judge_smoke_gpt4o_blocker_valid_json-marked_answer_turns-summary.md`
- `2026-06-14T165325Z-longmemeval-dspy-official_judge_smoke_gpt4o_blocker_valid_json-marked_answer_turns-metrics.json`
- `2026-06-14T165325Z-longmemeval-dspy-official_judge_smoke_gpt4o_blocker_valid_json-marked_answer_turns-judge-results.jsonl`

## Bridge sanity check with available model

The same judge path was tested with Codex model `gpt-5.5` to verify the adapter works when the model is supported.

Result:

```text
judge=False
judge_errors=0
judged_rows=1
```

Artifacts:

- `2026-06-14T165034Z-longmemeval-dspy-official_judge_smoke_gpt55_bridge-marked_answer_turns.jsonl`
- `2026-06-14T165034Z-longmemeval-dspy-official_judge_smoke_gpt55_bridge-marked_answer_turns-summary.md`
- `2026-06-14T165034Z-longmemeval-dspy-official_judge_smoke_gpt55_bridge-marked_answer_turns-judge-results.jsonl`

This proves the Codex-bridge adapter can produce row-level judge labels with a supported model, but it is **not** the official LongMemEval GPT-4o score.

## Conclusion

The official apples-to-apples LongMemEval rerun is blocked until a GPT-4o-capable evaluation path is available, for example:

1. an OpenAI API key usable by the official `evaluate_qa.py` script, or
2. a Codex bridge/profile/account that supports `gpt-4o`, or
3. an explicit decision to use a non-official judge model such as `gpt-5.5` and label it as non-official.

Do not report the prior heuristic scoreboard as LongMemEval accuracy.
