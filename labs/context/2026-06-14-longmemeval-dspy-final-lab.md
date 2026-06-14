# Context Module 12 — Simple DSPy on LongMemEval

## Metadata

- Date: 2026-06-14
- Course section: Context Engineering
- Module / lab: Module 12 — Evaluation / final LongMemEval lab, first slice
- Status: Attempted — tiny five-run DSPy reader slice
- Related files:
  - [`scripts/run_longmemeval_dspy.py`](./scripts/run_longmemeval_dspy.py)
  - [`results/2026-06-14T153321Z-longmemeval-dspy-marked_answer_turns_5run_slice-marked_answer_turns-summary.md`](./results/2026-06-14T153321Z-longmemeval-dspy-marked_answer_turns_5run_slice-marked_answer_turns-summary.md)
  - [`results/2026-06-14T155254Z-longmemeval-dspy-frozen-reader-policy-scoreboard.md`](./results/2026-06-14T155254Z-longmemeval-dspy-frozen-reader-policy-scoreboard.md)
  - [`results/2026-06-14T165034Z-longmemeval-dspy-official-judge-blocker.md`](./results/2026-06-14T165034Z-longmemeval-dspy-official-judge-blocker.md)
  - [`results/2026-06-14T170537Z-longmemeval-dspy-gpt54-judge-frozen-reader-scoreboard.md`](./results/2026-06-14T170537Z-longmemeval-dspy-gpt54-judge-frozen-reader-scoreboard.md)
  - [`results/2026-06-14T173702Z-longmemeval-dspy-structured-evidence-gpt54-scoreboard.md`](./results/2026-06-14T173702Z-longmemeval-dspy-structured-evidence-gpt54-scoreboard.md)
  - Local ignored dataset path: `labs/context/data/longmemeval/`

## Objective

Start the Context Engineering final lab using the real LongMemEval cleaned dataset rather than a toy fixture.

The first slice intentionally keeps the DSPy program simple: a typed `LongMemAnswer` signature receives a selected context, the question, and the question date, then returns a short answer grounded only in that context. The harness varies context policy around the DSPy program and records run-to-run variance.

## Hypothesis / expected failure mode

The immediate expectation was not leaderboard performance. The expected first failure mode was that a simple DSPy reader over a small LongMemEval slice would expose whether the bottleneck is retrieval/context selection, reader behavior, parsing, or budget.

For this first run, the selected policy was `marked_answer_turns`, an oracle-style policy over `longmemeval_oracle.json` that includes only turns marked by the dataset as answer-bearing. This is not a fair deployable retrieval method. It is a tiny upper-bound reader smoke test: if the model misses even with answer-bearing turns supplied, the next fix is reader/context formatting, not retrieval.

## Socratic prompts / hints used

- Prompt or hint 1: The final lab needs to isolate the context-construction policy: keep model, questions, rubric, and generation settings fixed while varying what context enters the model call.
- Prompt or hint 2: Start with a real LongMemEval slice and a simple DSPy program before adding retrieval, compaction, or structured memory complexity.
- What Ryan decided after the hints: Use DSPy again, pull the real LongMemEval data locally, ignore the large dataset files in git, and throw a simple DSPy program at the benchmark.

## Attempt

Downloaded the official cleaned LongMemEval files under an ignored local path:

```text
labs/context/data/longmemeval/
```

Added `.gitignore` coverage for:

```text
labs/context/data/
```

Implemented:

```text
labs/context/scripts/run_longmemeval_dspy.py
```

The script supports:

- DSPy `Predict` or `ChainOfThought` reader modules,
- Ollama-backed DSPy via `dspy.LM("ollama_chat/llama3:latest")`,
- context policies including `oracle`, `recent`, `answer_sessions`, `lexical_retrieval`, and `marked_answer_turns`,
- repeated runs for variance,
- JSONL, CSV, and Markdown summaries,
- lightweight local scoring using normalized substring match or token F1 >= 0.80.

After reviewing the LongMemEval scoring method, the harness was extended to support official-style evaluation artifacts:

- per-repeat `question_id` / `hypothesis` JSONL files compatible with the official one-hypothesis-per-question shape,
- LongMemEval v1 GPT-4o judge prompt templates from `evaluate_qa.py`,
- Codex-bridge judge fields (`judge_correct`, `judge_model`, `judge_provider`, `judge_raw_response`, `judge_error`),
- retrieval diagnostics (`recall_any@k`, `recall_all@k`, `ndcg_any@k`, `mrr`),
- optional embedding-based semantic-grounding diagnostics.
- structured context rendering via `--context-format structured`,
- an evidence-first reader via `--reader evidence_answer`, which emits `evidence_quote` plus final `answer`.

The local heuristic/F1 score is now a diagnostic only, not a LongMemEval score.

## Verification

Environment and syntax checks:

```sh
/tmp/agent-harness-dspy-venv/bin/python - <<'PY'
import dspy
print('dspy', getattr(dspy, '__version__', 'unknown'))
PY
/tmp/agent-harness-dspy-venv/bin/python -m py_compile labs/context/scripts/run_longmemeval_dspy.py
```

Relevant output:

```text
dspy 3.2.1
```

Five-run LongMemEval slice:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/context/scripts/run_longmemeval_dspy.py \
  --dataset labs/context/data/longmemeval/longmemeval_oracle.json \
  --condition marked_answer_turns_5run_slice \
  --context-policy marked_answer_turns \
  --limit 3 \
  --repeats 5 \
  --model ollama_chat/llama3:latest \
  --api-base http://localhost:11434 \
  --adapter chat \
  --temperature 0 \
  --max-tokens 512 \
  --max-context-chars 12000 \
  --max-turn-chars 4000
```

Relevant output:

```text
gpt4_2655b836 repeat=1 MISS f1=0.000 words=138 elapsed=0.53s
gpt4_2487a7cb repeat=1 MISS f1=0.000 words=154 elapsed=0.40s
gpt4_76048e76 repeat=1 OK f1=0.667 words=136 elapsed=0.37s
...
gpt4_2655b836 repeat=5 MISS f1=0.000 words=138 elapsed=0.43s
gpt4_2487a7cb repeat=5 MISS f1=0.000 words=154 elapsed=0.39s
gpt4_76048e76 repeat=5 OK f1=0.667 words=136 elapsed=0.41s
```

Summary:

```text
Rows: 15
Questions: 3
Repeats: 5
Accuracy: 0.333
Accuracy stdev: 0.471
Mean token F1: 0.222
Evidence hit rate: 1.000
Parse errors: 0
Mean context words: 142.7
Mean elapsed seconds: 0.42
```

Frozen-reader context-policy comparison, before any reader tuning:

```sh
for policy in answer_sessions lexical_retrieval recent all; do
  /tmp/agent-harness-dspy-venv/bin/python labs/context/scripts/run_longmemeval_dspy.py \
    --dataset labs/context/data/longmemeval/longmemeval_s_cleaned.json \
    --condition frozen_reader_s_first3_${policy} \
    --context-policy "$policy" \
    --limit 3 \
    --repeats 5 \
    --model ollama_chat/llama3:latest \
    --api-base http://localhost:11434 \
    --adapter chat \
    --predictor predict \
    --temperature 0 \
    --max-tokens 512 \
    --max-context-chars 12000 \
    --max-turn-chars 4000 \
    --top-k 3
done
```

Combined scoreboard:

| Policy | Dataset role | Rows | Questions | Repeats | Accuracy | Mean F1 | Evidence hit | Parse errors | Mean context words |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `marked_answer_turns` | oracle answer turns | 15 | 3 | 5 | 0.333 | 0.222 | 1.000 | 0 | 142.7 |
| `answer_sessions` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | 1.000 | 0 | 1883.3 |
| `lexical_retrieval` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.333 | 0 | 1965.3 |
| `recent` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.333 | 0 | 1928.3 |
| `all` | `s_cleaned` first3 | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0 | 1939.7 |

Scoreboard artifact:

- `results/2026-06-14T155254Z-longmemeval-dspy-frozen-reader-policy-scoreboard.md`

Official-style GPT-4o judge attempt:

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

The row-level judge error reported that the `gpt-4o` model is not supported when using the current Codex ChatGPT account. A separate one-row smoke using `--judge-model gpt-5.5` succeeded with `judge_errors=0`, proving the Codex-bridge adapter works with a supported model, but that result is not the official LongMemEval GPT-4o score.

Blocker artifact:

- `results/2026-06-14T165034Z-longmemeval-dspy-official-judge-blocker.md`

Non-official Codex `gpt-5.4` judged rerun:

After the GPT-4o path was blocked, Ryan explicitly chose Codex `gpt-5.4` as the judge. The same frozen reader and context policies were rerun with LongMemEval-style yes/no judge prompts via `--judge-provider codex-bridge --judge-model gpt-5.4`.

Scoreboard artifact:

- `results/2026-06-14T170537Z-longmemeval-dspy-gpt54-judge-frozen-reader-scoreboard.md`

Judged result:

| Policy | Dataset role | gpt-5.4 judge acc | Recall any@3 | Recall all@3 | Notes |
|---|---|---:|---:|---:|---|
| `marked_answer_turns` | oracle answer turns | 0.333 | 1.000 | 0.667 | Same 1/3 pattern as local heuristic. |
| `answer_sessions` | `s_cleaned` first3 | 0.000 | 1.000 | 1.000 | Correct sessions supplied; reader still failed. |
| `lexical_retrieval` | `s_cleaned` first3 | 0.000 | 0.333 | 0.333 | Retrieval and reader both weak. |
| `recent` | `s_cleaned` first3 | 0.000 | 0.333 | 0.000 | Recency missed most evidence. |
| `all` | `s_cleaned` first3 | 0.000 | 0.000 | 0.000 | Truncated context missed answer sessions on this slice. |

This is not the official LongMemEval GPT-4o score, but it does confirm the earlier failure mode under an LLM-judge-style metric.

Structured context + evidence-first reader rerun:

To address the reader/context-format failure, the harness was extended with:

- `--context-format structured`, adding question/date headers, session separators, turn numbers, speaker labels, and task instructions,
- `--reader evidence_answer`, a DSPy signature that asks for an `evidence_quote` before the final short `answer`.

A one-row smoke test showed the pattern before the full rerun:

| Variant | Policy | gpt-5.4 judge result | Note |
|---|---|---:|---|
| raw simple reader | `answer_sessions` | 0/1 | Existing shape missed. |
| structured simple reader | `answer_sessions` | 0/1 | Formatting alone was not enough. |
| structured evidence reader | `answer_sessions` | 1/1 | Evidence-first output rescued the first dev row. |

Then the same first-three policy comparison was rerun with the structured evidence reader.

Scoreboard artifact:

- `results/2026-06-14T173702Z-longmemeval-dspy-structured-evidence-gpt54-scoreboard.md`

Judged result:

| Policy | Dataset role | structured evidence gpt-5.4 acc | Prior frozen gpt-5.4 acc | Recall any@3 | Recall all@3 | Notes |
|---|---|---:|---:|---:|---:|---|
| `marked_answer_turns` | oracle answer turns | 0.333 | 0.333 | 1.000 | 0.667 | No net oracle-turn improvement. |
| `answer_sessions` | `s_cleaned` first3 | 0.333 | 0.000 | 1.000 | 1.000 | One of three dev questions rescued. |
| `lexical_retrieval` | `s_cleaned` first3 | 0.000 | 0.000 | 0.333 | 0.333 | Retrieval and reader still weak. |
| `recent` | `s_cleaned` first3 | 0.000 | 0.000 | 0.333 | 0.333 | Recency remains weak. |
| `all` | `s_cleaned` first3 | 0.000 | 0.000 | 0.000 | 0.000 | Truncated all-context still misses evidence. |

The best signal is `answer_sessions`: retrieval stayed perfect, while the reader improved from 0/3 to 1/3. That is a reader/context-format improvement, not a retrieval win.

## Result

- Outcome: Attempted — first real LongMemEval/DSPy slice ran end-to-end.
- What worked:
  - The real cleaned LongMemEval dataset is local and ignored by git.
  - The DSPy reader harness runs against LongMemEval records and writes inspectable artifacts.
  - The harness reports five-run variance, context size, latency, parse errors, evidence hit rate, and lightweight correctness.
  - The harness now writes official-compatible hypothesis files and can route LongMemEval-style judge prompts through Codex when the requested model is supported.
  - A non-official Codex `gpt-5.4` judged rerun completed with zero judge errors.
  - Structured context plus an evidence-first reader rescued one `answer_sessions` development question without changing retrieval.
- What failed or surprised me:
  - Even an oracle-style answer-turn context policy only scored 1/3 questions across all five repeats on the first slice.
  - Freezing the reader and comparing policies on the first three `longmemeval_s_cleaned.json` rows produced a dismal but useful baseline: `answer_sessions`, `lexical_retrieval`, `recent`, and truncated `all` all scored 0/3 across five repeats.
  - `answer_sessions` had evidence hit 1.0 and still scored 0.0, which is the clearest sign that the current reader/context format is a bottleneck before retrieval quality.
  - The two misses were stable at temperature 0, so this first result points to reader/context-format weakness, not stochastic variance.
  - A fuller oracle-context smoke produced adapter/truncation trouble before this run, reinforcing that LongMemEval needs staged context budgets rather than immediate full-context stuffing.
  - The requested apples-to-apples GPT-4o judge rerun is blocked because this Codex account does not support `gpt-4o` through `codex exec`.
  - The `gpt-5.4` judged rerun stayed ugly: oracle answer turns scored 1/3 and all first-three `s_cleaned` policies scored 0/3.
  - The structured evidence reader improved `answer_sessions` from 0/3 to 1/3, but did not improve retrieval-weak policies.
- What changed between expected and observed behavior:
  - The first useful lesson is narrower than the final claim. This run does not yet compare structured memory against context stuffing; it proves the benchmark/harness path works and shows the reader can fail even when evidence-bearing turns are present.
  - The earlier policy table should be read as a local heuristic baseline, not official LongMemEval accuracy.

## Recruiter-agent inspection notes

- Claim supported: Ryan started the Context Module 12 final lab against the real LongMemEval cleaned dataset with a simple frozen DSPy reader, five repeated oracle-turn runs, a first frozen-reader policy comparison before tuning, an attempted official GPT-4o judge path blocked by Codex model availability, a completed non-official Codex `gpt-5.4` judged rerun, and a first reader/context-format intervention that rescued one `answer_sessions` dev question.
- Evidence path: `scripts/run_longmemeval_dspy.py`, the `2026-06-14T153321Z` oracle-turn artifacts, the `2026-06-14T155*` frozen-reader policy artifacts, the frozen-reader policy scoreboard, and this note.
- Confidence: High that the script runs and records useful first-slice evidence; low that this tiny 3-question oracle-turn slice says anything broad about LongMemEval performance.
- Caveat: This first policy uses dataset-provided answer markers and is therefore an oracle diagnostic, not a deployable retrieval system. The `gpt-5.4` reruns are useful LLM-judge-style baselines but not the official LongMemEval GPT-4o score. The structured evidence improvement was measured on the already-seen first-three development slice.

## Next step

Inspect the two remaining `answer_sessions` failures, tune only on this development slice, then freeze the reader and validate on a fresh held-out slice such as `--offset 3 --limit 7`. Keep the `gpt-5.4` judged baseline as non-official evidence unless a GPT-4o-capable official judge route becomes available.
