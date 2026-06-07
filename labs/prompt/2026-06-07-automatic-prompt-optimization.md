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

## Result

- Outcome: Attempted / GEPA smoke passed, reliability redesign passed, optimization not yet successful
- What worked: The reusable prompt-template evaluator works; first-pass APE results are recorded; DSPy 3.2.1 installed in a temporary venv; local Ollama works through DSPy; `dspy.GEPA` ran with a score+feedback metric; the structured harness now records format, adapter, and math failures separately; repeated adapter checks produced no format/adapter failures across 24 structured row-evaluations.
- What failed or surprised me: First-pass APE did not beat the hand baseline. The local-only optimizer produced weak/generic candidates. The initial tiny GEPA smoke tied baseline at 1/4 and exposed practical issues. After the reliability redesign, the tiny structured GEPA smoke still showed no optimization win, but the failures were now cleanly classified as math failures instead of adapter/format failures. ChatAdapter still showed answer variance despite temperature 0.0.
- What changed between expected and observed behavior: The original hypothesis is not supported by first-pass APE or the tiny GEPA smoke. The best current explanation is that the dev slice is small/noisy and/or local Mistral's reasoning ability is the bottleneck; prompt wording alone has not moved the scoreboard yet. The harness is now reliable enough to separate that model-reasoning bottleneck from parser/schema noise, with JSONAdapter currently the more stable adapter on the checked slice.

## Recruiter-agent inspection notes

- Claim supported: Ryan is setting up a controlled prompt-optimization comparison rather than hand-tuning by vibes; the shared evaluator foundation has been smoke-tested; first-pass APE, a tiny GEPA/DSPy smoke, and a reliability-focused DSPy schema redesign are recorded with conservative non-win claims.
- Evidence path: This note, [`scripts/evaluate_gsm8k_prompt_ollama.py`](./scripts/evaluate_gsm8k_prompt_ollama.py), [`scripts/run_gsm8k_gepa_dspy_smoke.py`](./scripts/run_gsm8k_gepa_dspy_smoke.py), [`results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md`](./results/2026-06-07-ape-local-vs-hybrid-dev30-scoreboard.md), [`results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md`](./results/2026-06-07T150719Z-gsm8k-gepa-smoke-train1-4-val5-8-summary.md), [`results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md`](./results/2026-06-07T154424Z-gsm8k-gepa-structured-chat-train1-2-val5-6-summary.md), and [`results/2026-06-07-gsm8k-structured-adapter-stability-summary.md`](./results/2026-06-07-gsm8k-structured-adapter-stability-summary.md).
- Confidence: High that the harness/GEPA setup path is now inspectable and has explicit reliability tests; low that prompt optimization has improved this local model yet.
- Caveat: The GEPA runs are tiny setup smokes using local Mistral as both solver and reflection model; they should not be treated as benchmarks of GEPA's frontier performance.

## Next step

Run a slightly larger structured ChatAdapter smoke before any benchmark claim: train/val 4/4 or 8/8, solver tokens 768, reflection tokens 1024, and inspect failure counts. If failures remain mostly `math`, try a stronger reflection model next; if `format` or `adapter` returns, fix schema/adapter reliability before scaling. Do not compare GEPA to APE on held-out rows until the structured failure modes stay stable.
