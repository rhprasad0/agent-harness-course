# Automatic Prompt Optimization Lab

## Metadata

- Date: 2026-06-07
- Course section: Prompt Engineering
- Module / lab: Module 10 — Automatic Prompt Optimization
- Status: Starting
- Related files:
  - [`index.html`](../../index.html) — curriculum source for Module 10
  - [`scripts/run_gsm8k_ollama_eval.py`](./scripts/run_gsm8k_ollama_eval.py) — prior deterministic GSM8K baseline harness
  - [`scripts/run_gsm8k_self_consistency_ollama.py`](./scripts/run_gsm8k_self_consistency_ollama.py) — prior self-consistency harness
  - [`results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md) — previous N=1/3/5/10 curve

## Objective

Test whether automatic prompt optimization can improve a hand-written GSM8K reasoning prompt, and compare that improvement against the cost of search.

The curriculum lab asks for at least two optimization methods. This run will start with three tracks:

1. **Local-only optimizer** — local Ollama model proposes prompt candidates; local Ollama model solves GSM8K.
2. **Hybrid optimizer** — stronger assistant/frontier model proposes prompt candidates; local Ollama model solves GSM8K.
3. **GEPA / DSPy optimizer** — reflection-driven prompt evolution if dependency setup and local/provider configuration are practical.

## Hypothesis / expected failure mode

Ryan's pre-run hypothesis:

> APE/OPRO-style automatic prompt optimization will improve accuracy meaningfully.

Operationalized for this lab:

- A method supports the hypothesis if its best prompt improves held-out single-call accuracy by at least **+5 percentage points** over the hand-written baseline.
- A method is treated as weak or overfit if it improves the dev slice but not held-out rows.
- A method is treated as harmful if it raises parse failures or output-format errors enough to erase accuracy gains.

## Socratic prompts / hints used

- Prompt or hint 1: What should count as a meaningful improvement: dev-set gain, held-out gain, parse compliance, or cost-adjusted gain?
- Prompt or hint 2: Should the optimizer be local-only, hybrid with a stronger proposer, or both?
- What Ryan decided after the hints: run both local-only and hybrid comparisons, and include GEPA because it is the current frontier prompt-optimization method in the curriculum.

## Attempt

Planned controlled split:

| Slice | Rows | Purpose |
|---|---:|---|
| Dev/search | GSM8K test rows 1–30 | Prompt candidate search and optimizer feedback |
| Held-out | GSM8K test rows 31–100 | Final comparison against baseline |

Baseline prompt from prior GSM8K harness:

```text
Solve the following grade-school math word problem. Show your reasoning briefly, then end with exactly one line in this format:
FINAL_ANSWER: <number>

Question:
{question}
```

Prior reference result on the first 100 GSM8K test rows with `mistral:7b-instruct-q4_K_M`:

| Method | Accuracy | Notes |
|---|---:|---|
| Deterministic baseline, temperature 0 | 35/100 | Previous calibration run |
| Sampled N=1, temperature 0.7 | 36/100 | From self-consistency run |
| Self-consistency N=10, temperature 0.7 | 55/100 | Majority-vote ceiling/cost comparison |

Planned methods:

### Method A — APE-style candidate generation

1. Evaluate baseline on the 30-row dev slice.
2. Collect correct, wrong, and parse-fragile examples.
3. Ask the optimizer to propose candidate prompts.
4. Evaluate each candidate on the dev slice.
5. Promote the top candidates to held-out evaluation.

### Method B — OPRO-style scoreboard search

1. Maintain a prompt scoreboard with dev accuracy and failure notes.
2. Feed the scoreboard to the optimizer.
3. Ask for new candidates that should outperform the current best.
4. Repeat for a small number of rounds.
5. Evaluate the best final candidates on held-out rows.

### Method C — GEPA / DSPy reflection-driven optimization

GEPA is included as the frontier comparison if setup is practical. The important distinction is that GEPA should receive **textual feedback**, not only scalar accuracy.

Ryan chose a **gold-rationale-aware hybrid feedback** design for the first pass:

- always include deterministic mechanical feedback: predicted answer, gold answer, parse validity, and exact-match score;
- for wrong cases, ask an LLM judge to inspect the question, the full GSM8K gold solution, the gold final answer, the solver's full response, and the solver's parsed answer;
- defer overfitting diagnosis until there is evidence of overfitting rather than designing around a hypothetical failure too early.

The feedback rubric should use a stable controlled taxonomy:

| Label | Meaning |
|---|---|
| `correct` | Parsed answer matches gold |
| `format_error` | Answer may exist, but required final format is missing or broken |
| `parse_error` | Could not extract a numeric final answer |
| `setup_error` | Misread quantities, target, units, or relationships |
| `operation_error` | Chose the wrong math operation or equation |
| `arithmetic_error` | Right setup, wrong calculation |
| `unsupported_assumption` | Added facts not in the question |
| `incomplete_reasoning` | Stopped too early or skipped necessary steps |
| `other` | Judge cannot confidently classify |

Initial environment check on 2026-06-07 found:

```text
dspy: not installed
gepa: not installed
Python 3.10.12
```

So GEPA requires dependency setup before execution.

## Verification

First runnable step: build the **baseline prompt-template evaluator only**. This deliberately does not generate or optimize prompts yet. It creates the shared scoring foundation that APE, OPRO, and GEPA candidates must all pass through.

Created files:

- [`prompts/gsm8k_baseline_reasoning.txt`](./prompts/gsm8k_baseline_reasoning.txt)
- [`scripts/evaluate_gsm8k_prompt_ollama.py`](./scripts/evaluate_gsm8k_prompt_ollama.py)

Verification commands:

```sh
python3 -m py_compile labs/prompt/scripts/evaluate_gsm8k_prompt_ollama.py
python3 labs/prompt/scripts/evaluate_gsm8k_prompt_ollama.py --help
python3 labs/prompt/scripts/evaluate_gsm8k_prompt_ollama.py --limit 3 --offset 0 --num-predict 256 --temperature 0.0
```

Relevant output:

```text
row=001 pred='18' gold='18' correct=True parse=final_answer_marker elapsed=6.4s
row=002 pred='3' gold='3' correct=True parse=final_answer_marker elapsed=1.6s
row=003 pred='17' gold='70000' correct=False parse=final_answer_marker elapsed=1.9s

wrote labs/prompt/results/2026-06-07T140449Z-gsm8k-test-offset0-limit3-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning.jsonl
wrote labs/prompt/results/2026-06-07T140449Z-gsm8k-test-offset0-limit3-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning-summary.md
```

Smoke-test summary:

- 2/3 correct on GSM8K test rows 1–3.
- All 3 responses used the requested `FINAL_ANSWER` marker.
- The wrong case was a reasoning/answer failure, not a parse failure.

Dev/search baseline run:

```sh
python3 labs/prompt/scripts/evaluate_gsm8k_prompt_ollama.py --limit 30 --offset 0 --num-predict 256 --temperature 0.0 --prompt-id baseline_reasoning_dev30
```

Relevant output:

```text
- Result: 8/30 correct (26.7%)
- Average elapsed: 1.47s/question
- Average prompt tokens reported by Ollama: 116.4
- Average completion tokens reported by Ollama: 181.6
- Parse statuses: 29 `final_answer_marker`, 1 `last_number_fallback`
```

Artifacts:

- [`results/2026-06-07T143510Z-gsm8k-test-offset0-limit30-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning_dev30-summary.md`](./results/2026-06-07T143510Z-gsm8k-test-offset0-limit30-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning_dev30-summary.md)
- [`results/2026-06-07T143510Z-gsm8k-test-offset0-limit30-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning_dev30.jsonl`](./results/2026-06-07T143510Z-gsm8k-test-offset0-limit30-ollama-mistral-7b-instruct-q4_K_M-prompt-baseline_reasoning_dev30.jsonl)

This 8/30 dev score is the first fixed-harness scoreboard entry that future prompt candidates must beat under the same rows/settings.

APE mixed-example briefing:

Ryan chose **mixed correct + wrong examples** for the first APE-style candidate generation step. This preserves visible examples of what the baseline already does well while showing failures the optimizer should target.

Created briefing artifact:

- [`results/2026-06-07-ape-mixed-example-briefing.md`](./results/2026-06-07-ape-mixed-example-briefing.md)

Briefing contents:

- fixed evaluator conditions,
- baseline dev score: 8/30,
- 4 correct baseline examples,
- 8 wrong baseline examples,
- instruction that future candidate prompts must preserve `FINAL_ANSWER: <number>` and be evaluated through the same harness before any improvement claim.

First APE candidate pass:

Ryan chose to generate/evaluate both local-only and hybrid candidates in the same pass. Candidate prompt files:

- [`prompts/ape_local_1_john.txt`](./prompts/ape_local_1_john.txt)
- [`prompts/ape_local_2_jane.txt`](./prompts/ape_local_2_jane.txt)
- [`prompts/ape_local_3_david.txt`](./prompts/ape_local_3_david.txt)
- [`prompts/ape_hybrid_units_equation_check.txt`](./prompts/ape_hybrid_units_equation_check.txt)
- [`prompts/ape_hybrid_quantity_checklist.txt`](./prompts/ape_hybrid_quantity_checklist.txt)
- [`prompts/ape_hybrid_goal_given_plan.txt`](./prompts/ape_hybrid_goal_given_plan.txt)

The local optimizer's raw generation is preserved at [`results/2026-06-07-local-ape-candidate-generation-raw.md`](./results/2026-06-07-local-ape-candidate-generation-raw.md). It produced generic prompts and formatting issues, which is useful evidence that local-only prompt generation may be weak in this setup.

Scoreboard artifact:

- [`results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md`](./results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md)

Dev-30 results:

| Prompt ID | Source | Correct | Accuracy | Notes |
|---|---|---:|---:|---|
| `baseline_reasoning_dev30` | hand baseline | 8/30 | 26.7% | best format compliance: 29/30 final marker |
| `ape_local_1_john` | local APE | 8/30 | 26.7% | tied baseline, more fallback parsing |
| `ape_local_2_jane` | local APE | 7/30 | 23.3% | under baseline |
| `ape_local_3_david` | local APE | 8/30 | 26.7% | tied baseline |
| `ape_hybrid_units_equation_check` | hybrid APE | 7/30 | 23.3% | under baseline, many fallback parses |
| `ape_hybrid_quantity_checklist` | hybrid APE | 8/30 | 26.7% | tied baseline, many fallback parses |
| `ape_hybrid_goal_given_plan` | hybrid APE | 8/30 | 26.7% | tied baseline, more fallback parsing than baseline |

Interpretation: first-pass APE did **not** improve over the hand baseline on the fixed dev slice. More structured prompts often reduced final-marker compliance or increased fallback parsing. This does not falsify all prompt optimization; it says the first APE candidate set did not support the hypothesis.

If GEPA/DSPy is added later:

```sh
python3 - <<'PY'
import dspy
print(dspy.__version__)
print(hasattr(dspy, 'GEPA'))
PY
```

GEPA / DSPy setup smoke:

Created dependency note and smoke script:

- [`requirements-dspy.txt`](./requirements-dspy.txt) — pins `dspy==3.2.1` and `pytest==9.0.3` for the reliability tests
- [`scripts/run_gsm8k_gepa_dspy_smoke.py`](./scripts/run_gsm8k_gepa_dspy_smoke.py)

Environment setup used for the smoke run:

```sh
python3 -m venv /tmp/agent-harness-dspy-venv
/tmp/agent-harness-dspy-venv/bin/python -m pip install dspy==3.2.1
```

DSPy capability check:

```text
dspy 3.2.1
has_GEPA True
GEPA_sig (metric: ..., auto=None, max_full_evals=None, max_metric_calls=None, reflection_lm=None, ...)
```

A minimal DSPy local-Ollama call also succeeded:

```text
Prediction(answer='5')
```

GEPA smoke command:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py
```

GEPA smoke artifact:

- [`results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md`](./results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md)
- [`results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8.json`](./results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8.json)

Smoke result:

| Run | Validation score | Notes |
|---|---:|---|
| DSPy baseline program | 1/4 | local Ollama/DSPy path works |
| GEPA-compiled program | 1/4 | GEPA ran, but no improvement on tiny validation slice |

Important setup observations:

- `dspy.GEPA` can run locally with Ollama and a metric returning `dspy.Prediction(score, feedback)`.
- The tiny smoke used local Mistral as both solver and reflection model, so weak reflection is expected.
- Several DSPy calls warned that model responses were truncated at `max_tokens=256`, and some GEPA candidate programs caused adapter parse errors when the local model produced reasoning without the expected `answer` field.
- This is a useful framework-learning result, not an optimization win.

## Reliability redesign

After the first GEPA smoke, we redesigned the DSPy harness around output reliability before scaling the optimizer.

Changes:

- Replaced implicit `ChainOfThought(question -> answer)` with an explicit structured signature: `question -> reasoning: str, answer: int`.
- Used `dspy.Predict` with explicit reasoning and integer answer fields so the schema is visible instead of relying on ChainOfThought's hidden rationale-field insertion.
- Added `--adapter chat/json` to compare DSPy adapter behavior directly.
- Increased default generation budgets to reduce truncation noise: solver 768 tokens, reflection 1024 tokens.
- Changed the GEPA metric to classify failures as `correct`, `math`, `format`, or `adapter`, so the optimizer feedback can distinguish wrong arithmetic from schema/parse failures.
- Added tests for schema shape, failure classification, adapter factory behavior, and exception capture.

RED/GREEN evidence:

```text
# RED
/tmp/agent-harness-dspy-venv/bin/python -m pytest tests/test_gsm8k_gepa_reliability.py -q
4 failed

# GREEN
/tmp/agent-harness-dspy-venv/bin/python -m pytest tests -q
8 passed
```

Structured smoke artifacts:

- [`results/2026-06-07T154357Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md`](./results/2026-06-07T154357Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md) — ChatAdapter baseline-only structured reliability check, 1/2 with one math failure.
- [`results/2026-06-07T154410Z-gsm8k-gepa-structured-json-train1-2-val5-6-summary.md`](./results/2026-06-07T154410Z-gsm8k-gepa-structured-json-train1-2-val5-6-summary.md) — JSONAdapter baseline-only structured reliability check, 0/2 with two math failures.
- [`results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md`](./results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md) — ChatAdapter GEPA structured smoke, 0/2 baseline and 0/2 compiled, both failing as math rather than parser/format failures.

Interpretation:

- The redesign improved observability: failures are now classified cleanly instead of being mixed parser/math mush.
- The tiny GEPA run still did not improve accuracy; on this slice, all failures were math failures after the schema stabilized.
- The baseline-only and GEPA runs differed on one row despite temperature 0.0, so tiny local-model smoke scores should be treated as harness checks, not benchmark claims.

## Adapter / reliability stability check

Before scaling question count, we ran three repeated structured baseline-only smokes per adapter on the same four validation rows.

Command pattern:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py \
  --skip-gepa \
  --adapter chat|json \
  --train-limit 2 \
  --val-offset 4 \
  --val-limit 4 \
  --solver-max-tokens 768 \
  --reflection-max-tokens 1024
```

Summary artifact:

- [`results/2026-06-07-gsm8k-structured-adapter-stability-summary.md`](./results/2026-06-07-gsm8k-structured-adapter-stability-summary.md)

Aggregate result:

| Adapter | Repeat scores | Total failure counts across 12 row-evals | Stability read |
|---|---:|---|---|
| `chat` | `1/4`, `0/4`, `0/4` | `{'correct': 1, 'math': 11}` | Schema/adapter stable, answers not fully deterministic |
| `json` | `0/4`, `0/4`, `0/4` | `{'math': 12}` | Schema/adapter stable, answers deterministic on this slice |

Interpretation:

- No `format` or `adapter` failures appeared in 24 structured row-evaluations, so the schema redesign appears stable enough for the next small experiment.
- The remaining failures are math failures, not parse failures.
- `JSONAdapter` was more deterministic on this slice; `ChatAdapter` produced one correct answer once but also varied on rows 5 and 8.
- Conservative next step: use `json` if the next run prioritizes clean output stability; use `chat` only if a slightly larger check shows a real accuracy advantage.

## JSON + GPT-5.4 Codex-bridge reflection smoke

Next, we kept the solver fixed as local Mistral and used the Codex bridge only for GEPA reflection.

Bridge discovery:

```sh
curl -sS http://kube1.lan:4001/v1/models
```

Observed model IDs included:

```text
gpt-5.5
gpt-5.4
gpt-5.4-mini
gpt-5.3-codex
gpt-5.2-codex
```

A direct chat-completions smoke to `gpt-5.4` returned `bridge-ok`. DSPy/LiteLLM required a non-empty dummy `api_key` even though the bridge endpoint itself did not need real OpenAI auth, so the harness uses a placeholder such as `sk-noauth` and records only `reflection_api_key_set: true`, not the value.

Harness changes:

- Added separate solver and reflection LM configuration.
- Solver remains local Ollama Mistral.
- Reflection can now use `--reflection-provider openai-compatible`, `--reflection-model gpt-5.4`, and `--reflection-base-url http://kube1.lan:4001/v1`.
- Added tests proving the LM factory builds `ollama_chat/...` for the solver and `openai/gpt-5.4` for the bridge reflector.

First 4-row JSON/Codex-reflection attempt:

- Artifact: [`results/2026-06-07T160316Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md`](./results/2026-06-07T160316Z-gsm8k-gepa-structured-json-train1-2-val5-8-summary.md)
- Result: baseline `0/4`, compiled `0/4`, failure counts `{'math': 3, 'adapter': 1}`.
- Interpretation: row 7 still triggered local Mistral repetition/truncation under JSONAdapter. This is a solver/schema stress failure, not a reflection-model failure.

Targeted reflection smoke with failing train rows:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py \
  --adapter json \
  --train-offset 4 \
  --train-limit 2 \
  --val-offset 4 \
  --val-limit 2 \
  --solver-max-tokens 768 \
  --reflection-provider openai-compatible \
  --reflection-model gpt-5.4 \
  --reflection-base-url http://kube1.lan:4001/v1 \
  --reflection-api-key sk-noauth \
  --reflection-temperature 0.7 \
  --reflection-max-tokens 1536 \
  --max-metric-calls 8
```

Artifact:

- [`results/2026-06-07T160415Z-gsm8k-gepa-structured-json-train5-6-val5-6-summary.md`](./results/2026-06-07T160415Z-gsm8k-gepa-structured-json-train5-6-val5-6-summary.md)

Result:

| Run | Score | Failure counts |
|---|---:|---|
| Structured JSON baseline | `0/2` | `{'math': 2}` |
| GEPA compiled with GPT-5.4 reflection | `2/2` | `{'correct': 2}` |

GEPA proposed a concrete improved instruction that emphasized reading the required quantity, matching operations to wording, handling per-item/per-rate patterns, subtracting already-used amounts, and treating every-second-item discounts carefully.

Interpretation:

- This is the first positive GEPA signal in the lab.
- It is intentionally tiny and uses the same rows for train and validation, so it is not a benchmark or held-out win.
- It does support the bottleneck hypothesis: stronger reflection plus cleaner JSON failure feedback can produce a useful prompt mutation where local-only reflection did not.

## Row 7 guard and doubled held-out GEPA pre-flight

Row 7 previously exposed a JSONAdapter stress failure: local Mistral looped on bad algebra and never emitted the required `answer` field. We added a narrow direct-arithmetic guard to the structured signature: work forward from known quantities, compute named quantities before summing, avoid simultaneous equations, keep reasoning short, and always emit both JSON fields.

Targeted row-7 artifact:

- [`results/2026-06-07T162005Z-gsm8k-gepa-structured-json-train1-1-val7-7-summary.md`](./results/2026-06-07T162005Z-gsm8k-gepa-structured-json-train1-1-val7-7-summary.md)

Result: row 7 changed from `adapter` failure to parseable `math` failure (`pred=0`, `gold=260`). This is diagnostic progress, not a solved reasoning problem.

Doubled held-out pre-flight command:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py \
  --adapter json \
  --train-offset 4 \
  --train-limit 8 \
  --val-offset 12 \
  --val-limit 16 \
  --reflection-provider openai-compatible \
  --reflection-model gpt-5.4 \
  --reflection-base-url http://kube1.lan:4001/v1 \
  --reflection-api-key sk-noauth \
  --solver-max-tokens 1536 \
  --reflection-max-tokens 1536 \
  --max-metric-calls 48
```

Artifact:

- [`results/2026-06-07T162311Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T162311Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md)

Held-out result:

| Run | Score | Failure counts | Correct rows |
|---|---:|---|---|
| Structured JSON baseline | `3/16` | `{'math': 13, 'correct': 3}` | 20, 24, 26 |
| GEPA compiled with GPT-5.4 reflection | `3/16` | `{'math': 13, 'correct': 3}` | 20, 24, 26 |

Interpretation:

- No `adapter` or `format` failures appeared on the held-out slice, so the JSON schema is stable enough for a larger run with Mistral.
- GEPA proposed multiple plausible instruction mutations, but none were accepted as improving the validation score; compiled matched baseline exactly.
- The current Mistral bottleneck is no longer parsing. It is local Mistral's arithmetic/word-problem reasoning under single-call JSON output.
- Scaling is safe from a harness perspective, but not promising as an optimization-win path unless we add a stronger solver, repeated sampling, or a more targeted dev/validation design.

## Llama2 and Llama3 solver comparisons on the same split

Ryan asked to rerun the exact doubled split with `llama2:7b-chat-q4_0` as the solver while keeping JSONAdapter and GPT-5.4 reflection fixed. After Llama2 proved too parser-fragile, we also pulled/refreshed `llama3:latest` and ran the same split.

Command differences:

```sh
# Llama2 run
--model llama2:7b-chat-q4_0

# Llama3 run
/home/ryan/.local/bin/ollama pull llama3
--model llama3:latest
```

Artifacts:

- Llama2: [`results/2026-06-07T163004Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T163004Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md)
- Llama3: [`results/2026-06-07T163847Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T163847Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md)

Held-out result:

| Solver | Run | Score | Failure counts | Correct rows |
|---|---|---:|---|---|
| Mistral 7B | Structured JSON baseline | `3/16` | `{'math': 13, 'correct': 3}` | 20, 24, 26 |
| Mistral 7B | GEPA compiled | `3/16` | `{'math': 13, 'correct': 3}` | 20, 24, 26 |
| Llama2 7B Chat | Structured JSON baseline | `0/16` | `{'adapter': 12, 'math': 4}` | none |
| Llama2 7B Chat | GEPA compiled | `2/16` | `{'adapter': 8, 'math': 6, 'correct': 2}` | 23, 24 |
| Llama3 latest | Structured JSON baseline | `10/16` | `{'math': 6, 'correct': 10}` | 14, 15, 17, 19, 23, 24, 25, 26, 27, 28 |
| Llama3 latest | GEPA compiled | `10/16` | `{'math': 6, 'correct': 10}` | 14, 15, 17, 19, 23, 24, 25, 26, 27, 28 |

Interpretation:

- Llama2 was much less JSON-compliant than Mistral on this DSPy signature: baseline had 12 adapter failures out of 16.
- GPT-5.4 reflection improved Llama2's compiled program from `0/16` to `2/16`, rescuing rows 23 and 24 and reducing adapter failures from 12 to 8.
- Llama3 was JSON-stable and much stronger on this slice: `10/16` with no adapter/format failures.
- GEPA did not improve Llama3 on this split; compiled matched baseline exactly, and many GEPA iterations skipped because sampled minibatches were already perfect.
- Llama3 is likely too strong for this small held-out slice if the lab goal is to demonstrate prompt optimization gains, but it is useful as a cleaner middle/upper-bound solver below `gpt-oss:20b`.
- For Llama2, the next bottleneck is JSON/schema compliance before math reasoning. For Mistral, the next bottleneck is math reasoning after schema compliance. For Llama3, the bottleneck is finding a harder slice or a method beyond prompt-only GEPA.

## Llama3 larger split

Ryan requested a larger Llama3 run with 100 training examples and 200 validation examples.

Command shape:

```sh
/tmp/agent-harness-dspy-venv/bin/python labs/prompt/scripts/run_gsm8k_gepa_dspy_smoke.py \
  --model llama3:latest \
  --adapter json \
  --train-offset 4 \
  --train-limit 100 \
  --val-offset 104 \
  --val-limit 200 \
  --reflection-provider openai-compatible \
  --reflection-model gpt-5.4 \
  --reflection-base-url http://kube1.lan:4001/v1 \
  --reflection-api-key sk-noauth \
  --solver-max-tokens 1536 \
  --reflection-max-tokens 1536 \
  --max-metric-calls 600
```

Artifact:

- [`results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md`](./results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md)

Held-out result:

| Solver | Split | Run | Score | Failure counts | Row changes |
|---|---|---|---:|---|---|
| Llama3 latest | train 5–104 / val 105–304 | Structured JSON baseline | `138/200` | `{'correct': 138, 'math': 62}` | — |
| Llama3 latest | train 5–104 / val 105–304 | GEPA compiled | `138/200` | `{'correct': 138, 'math': 62}` | 0 rescued, 0 broken |

Interpretation:

- The larger split confirms the small-split read: Llama3 is JSON-stable and substantially stronger than Mistral/Llama2.
- There were no `adapter` or `format` failures in either baseline or compiled outputs.
- GEPA explored candidate prompt mutations and one candidate scored `139/200` during a full validation eval, but the final compiled program selected by aggregate score tied the baseline exactly at `138/200`.
- Prompt-only GEPA is not producing a durable held-out improvement for Llama3 under this single-call JSON solver setup.
- The next useful step is likely failure clustering or self-consistency on Llama3, not more blind GEPA budget.

## Result

- Outcome: Attempted / first positive GEPA mechanism smoke; doubled held-out Mistral pre-flight found no generalization win; same split with Llama2 showed a small GEPA gain from `0/16` to `2/16` but remained parser-heavy; small same split with Llama3 reached `10/16` but showed no GEPA lift; larger Llama3 split reached `138/200` and also showed no final GEPA lift.
- What worked: The reusable prompt-template evaluator works; first-pass APE results are recorded; DSPy 3.2.1 installed in a temporary venv; local Ollama works through DSPy; `dspy.GEPA` ran with a score+feedback metric; the structured harness now records format, adapter, and math failures separately; repeated adapter checks produced no format/adapter failures across 24 structured row-evaluations; GPT-5.4 via the Codex bridge produced a useful GEPA mutation on a targeted 2-row smoke; the row-7 guard converted a runaway adapter failure into a clean math failure; the doubled Mistral held-out pre-flight had zero adapter/format failures; the Llama2 rerun showed GPT-5.4 reflection can improve a weaker parser-heavy solver from no correct rows to two correct rows; Llama3 provided a clean stronger-solver comparison with no parser failures across both small and larger splits.
- What failed or surprised me: First-pass APE did not beat the hand baseline. The local-only optimizer produced weak/generic candidates. The initial tiny GEPA smoke tied baseline at 1/4 and exposed practical issues. After the reliability redesign, the tiny structured GEPA smoke still showed no optimization win, but the failures were cleanly classified. ChatAdapter still showed answer variance despite temperature 0.0. JSONAdapter can still trigger local-model reasoning failures, but the guard reduced schema/runaway failure on row 7. The doubled held-out GPT-5.4-reflection run tied Mistral baseline at 3/16. Llama2 was far less JSON-compliant than Mistral on the same signature. Llama3 was strong and clean, but prompt-only GEPA did not produce a final held-out improvement even at 200 validation examples.
- What changed between expected and observed behavior: The original broad hypothesis is not supported by first-pass APE, local-only GEPA, or the held-out Mistral/Llama3 GPT-5.4-reflection pre-flights. The targeted GPT-5.4-reflection smoke and Llama2 rerun support a narrower hypothesis: stronger reflection plus clean feedback can produce useful instruction mutations for specific weak-solver failure modes. Held-out evidence still does not show a strong generalized improvement from prompt-only GEPA.

## Recruiter-agent inspection notes

- Claim supported: Ryan is setting up a controlled prompt-optimization comparison rather than hand-tuning by vibes; the shared evaluator foundation has been smoke-tested; first-pass APE, local GEPA, adapter stability, row-7 guard behavior, a GPT-5.4-reflection mechanism smoke, a doubled Mistral held-out pre-flight, a same-split Llama2 solver comparison, and small/large Llama3 solver comparisons are recorded with conservative claims.
- Evidence path: This note, [`scripts/evaluate_gsm8k_prompt_ollama.py`](./scripts/evaluate_gsm8k_prompt_ollama.py), [`scripts/run_gsm8k_gepa_dspy_smoke.py`](./scripts/run_gsm8k_gepa_dspy_smoke.py), [`results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md`](./results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md), [`results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md`](./results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md), [`results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md`](./results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md), [`results/2026-06-07-gsm8k-structured-adapter-stability-summary.md`](./results/2026-06-07-gsm8k-structured-adapter-stability-summary.md), [`results/2026-06-07T160415Z-gsm8k-gepa-structured-json-train5-6-val5-6-summary.md`](./results/2026-06-07T160415Z-gsm8k-gepa-structured-json-train5-6-val5-6-summary.md), [`results/2026-06-07T162005Z-gsm8k-gepa-structured-json-train1-1-val7-7-summary.md`](./results/2026-06-07T162005Z-gsm8k-gepa-structured-json-train1-1-val7-7-summary.md), [`results/2026-06-07T162311Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T162311Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md), [`results/2026-06-07T163004Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T163004Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md), [`results/2026-06-07T163847Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md`](./results/2026-06-07T163847Z-gsm8k-gepa-structured-json-train5-12-val13-28-summary.md), and [`results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md`](./results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md).
- Confidence: High that the harness/GEPA setup path is now inspectable and has explicit reliability tests; high that JSON output is stable enough for Mistral and Llama3 larger runs; low that JSON output is stable enough for Llama2 without more schema work; medium that stronger reflection can help targeted failure classes; low that prompt optimization alone improves held-out performance with these local 7B single-call solvers.
- Caveat: The positive GPT-5.4-reflection smoke is a tiny same-row train/validation check; the doubled Mistral held-out pre-flight tied baseline; the Llama2 run improved from `0/16` to `2/16` but remained dominated by adapter failures; the Llama3 runs were clean but tied baseline at both `10/16` and `138/200`.

## Next step

Choose the next scaling path deliberately:

1. **Harness-scale path:** the larger Llama3 run is now complete; further blind scaling is unlikely to teach much unless the goal is negative evidence.
2. **Capability path:** add self-consistency around the compiled prompt, then compare against the existing N=10 self-consistency ceiling.
3. **Diagnostic path:** inspect the Mistral math failures, Llama2 adapter failures, or Llama3 remaining 62 larger-split math failures, cluster them by error type, and build a smaller targeted train/validation split before spending more GEPA calls.
