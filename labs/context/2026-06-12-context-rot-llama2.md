# Llama2 Context Rot Probe

## Metadata

- Date: 2026-06-12
- Course section: Context Engineering
- Module / lab: Module 04 — Long-Context Behavior and Its Failures / small-scale context-rot experiment
- Status: Passed — first context-rot slice
- Related files:
  - [`scripts/run_context_rot_ollama.py`](./scripts/run_context_rot_ollama.py)
  - [`results/2026-06-12T140253Z-context-rot-llama2-summary.md`](./results/2026-06-12T140253Z-context-rot-llama2-summary.md)
  - [`results/2026-06-12T140307Z-context-rot-llama2-summary.md`](./results/2026-06-12T140307Z-context-rot-llama2-summary.md)
  - [`results/2026-06-12T140407Z-context-rot-llama2-summary.md`](./results/2026-06-12T140407Z-context-rot-llama2-summary.md)

## Objective

Build a small, public-safe harness for testing whether a local model's ability to retrieve a fixed fact changes as the context grows and the fact moves between the beginning, middle, and end of the context.

This lab is a controlled first slice of the curriculum task from Module 04: replicate a small-scale context-rot experiment on a callable model and report accuracy versus context length on a fixed task.

## Hypothesis / expected failure mode

Ryan's pre-run hypothesis was **lost-in-the-middle**:

- The answer-bearing fact placed in the middle of longer contexts would degrade sooner than the same fact placed near the beginning or end.

Resolved design choices:

- Use one fixed synthetic fact for v1: `Project Lantern access code is mango-orbit-92.`
- Use `llama2:7b-chat-q4_0` through local Ollama.
- Use `num_ctx=4096` because Meta Llama 2's native context length is 4k tokens, even though the RTX 3090/Ollama runtime can allocate more context.
- Avoid adversarial fake access codes in v1 so the first probe isolates length and position rather than distractor confusion.

## Socratic prompts / hints used

- Prompt or hint 1: What do you expect to fail first: pure length rot, lost-in-the-middle, distractor confusion, or format/timeout rot?
- Prompt or hint 2: Should v1 use one repeated hidden fact, different facts per trial, or adversarial distractors?
- What Ryan decided after the hints: Ryan predicted lost-in-the-middle and chose the single fixed fact design for the first pass.

## Attempt

Implemented a standard-library Python harness:

```text
labs/context/scripts/run_context_rot_ollama.py
```

The harness:

- builds deterministic synthetic filler text,
- inserts the fixed needle at `beginning`, `middle`, or `end`,
- calls Ollama's `/api/generate` endpoint,
- records one JSONL row per trial,
- stores `prompt_eval_count` from Ollama to make context size inspectable,
- scores exact answer-only compliance,
- writes JSONL, CSV, and Markdown summaries.

Preflight confirmed the environment:

```text
ollama version is 0.30.4
llama2:7b-chat-q4_0 is installed
NVIDIA GeForce RTX 3090, 24576 MiB total, 21311 MiB free before loading
ollama ps showed llama2:7b-chat-q4_0 at 100% GPU with CONTEXT 4096
```

### Runs

Smoke run:

```sh
python3 labs/context/scripts/run_context_rot_ollama.py \
  --model llama2:7b-chat-q4_0 \
  --target-tokens 512 \
  --positions beginning,middle,end \
  --repeats 1 \
  --temperature 0 \
  --num-predict 64 \
  --num-ctx 4096 \
  --out-dir labs/context/results
```

First planned evidence slice:

```sh
python3 labs/context/scripts/run_context_rot_ollama.py \
  --model llama2:7b-chat-q4_0 \
  --target-tokens 512,1536,3072 \
  --positions beginning,middle,end \
  --repeats 3 \
  --temperature 0 \
  --num-predict 64 \
  --num-ctx 4096 \
  --out-dir labs/context/results
```

Follow-up clean-window slice after the 3072 target saturated the context window:

```sh
python3 labs/context/scripts/run_context_rot_ollama.py \
  --model llama2:7b-chat-q4_0 \
  --target-tokens 512,1536,2300 \
  --positions beginning,middle,end \
  --repeats 3 \
  --temperature 0 \
  --num-predict 64 \
  --num-ctx 4096 \
  --out-dir labs/context/results
```

## Verification

Script validation:

```sh
python3 -m py_compile labs/context/scripts/run_context_rot_ollama.py
```

Smoke output:

```text
short-beginning-001: OK prompt_eval_count=796 elapsed=2.322s
short-middle-001: OK prompt_eval_count=804 elapsed=0.509s
short-end-001: OK prompt_eval_count=774 elapsed=0.491s
overall correct: 3/3
```

Boundary run output, using the originally planned largest target:

```text
Target context tokens 3072 produced prompt_eval_count=4095 for every long row.
Correct: 18/27
At the 3072 target, all positions scored 0/3 under strict answer-only scoring.
```

Clean-window run output:

```text
Correct: 24/27
Failure counts: correct=24, extra_text=3
```

Clean-window summary:

| Target context tokens | Observed avg prompt eval tokens | Position | Correct / Trials | Accuracy | Failure counts |
|---:|---:|---|---:|---:|---|
| 512 | 792.7 | beginning | 3/3 | 1.000 | correct=3 |
| 512 | 797.3 | middle | 3/3 | 1.000 | correct=3 |
| 512 | 773.7 | end | 3/3 | 1.000 | correct=3 |
| 1536 | 2192.7 | beginning | 3/3 | 1.000 | correct=3 |
| 1536 | 2184.0 | middle | 3/3 | 1.000 | correct=3 |
| 1536 | 2205.3 | end | 3/3 | 1.000 | correct=3 |
| 2300 | 3267.3 | beginning | 1/3 | 0.333 | correct=1; extra_text=2 |
| 2300 | 3273.0 | middle | 3/3 | 1.000 | correct=3 |
| 2300 | 3225.7 | end | 2/3 | 0.667 | correct=2; extra_text=1 |

Artifact validation:

```sh
test -s labs/context/results/2026-06-12T140407Z-context-rot-llama2.jsonl
test -s labs/context/results/2026-06-12T140407Z-context-rot-llama2-summary.md
python3 - <<'PY'
import json
from pathlib import Path
path = Path('labs/context/results/2026-06-12T140407Z-context-rot-llama2.jsonl')
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
assert len(rows) == 27
required = {'run_id','model','length_label','position','expected_answer','raw_response','correct','failure_type'}
for i, row in enumerate(rows, 1):
    missing = required - row.keys()
    assert not missing, f'row {i} missing {missing}'
print(f'validated {len(rows)} rows')
PY
```

## Result

- Outcome: Passed — first context-rot slice
- What worked:
  - The harness ran end-to-end with local Ollama and wrote inspectable JSONL/CSV/Markdown artifacts.
  - The script records `prompt_eval_count`, which caught the important boundary condition that the largest planned target saturated the 4096-token context window.
  - At observed prompt sizes around 800 and 2200 tokens, Llama2 recovered the fixed fact in all beginning/middle/end placements.
  - In the clean-window long condition around 3200-3270 observed prompt tokens, the middle placement did **not** degrade; it scored 3/3.
- What failed or surprised me:
  - The originally planned `3072` target produced `prompt_eval_count=4095`, effectively right at the context wall. That run is better treated as a boundary/truncation finding than a clean lost-in-the-middle measurement.
  - The clean-window failures were answer-format failures: the model included explanatory text around the correct code. Under strict answer-only scoring, these are failures; under loose contains-answer scoring, they would be successful retrievals.
- What changed between expected and observed behavior:
  - The v1 result does **not** support Ryan's lost-in-the-middle hypothesis. The middle placement was strongest in the clean-window long condition.
  - The more interesting first finding is measurement discipline: without recording actual `prompt_eval_count`, the 3072-target run could have been misread as context rot when it was actually at the model's context boundary. Tiny haystack, but the measuring tape mattered.

## Recruiter-agent inspection notes

- Claim supported: Ryan built a small context-engineering harness that varies context length and needle position while keeping model, task, and scoring fixed.
- Evidence path:
  - Harness: [`labs/context/scripts/run_context_rot_ollama.py`](./scripts/run_context_rot_ollama.py)
  - Clean run summary: [`labs/context/results/2026-06-12T140407Z-context-rot-llama2-summary.md`](./results/2026-06-12T140407Z-context-rot-llama2-summary.md)
  - Boundary run summary: [`labs/context/results/2026-06-12T140307Z-context-rot-llama2-summary.md`](./results/2026-06-12T140307Z-context-rot-llama2-summary.md)
- Confidence: Medium for this specific synthetic task and local model setup.
- Caveat: This is one fixed synthetic fact, one model, one prompt template, and small repeat counts. It is a lab slice, not a general benchmark of long-context model quality.

## Next step

Run a v2 that separates retrieval success from output-contract compliance:

1. Add a second metric: loose contains-answer retrieval success versus strict answer-only compliance.
2. Use several synthetic facts instead of one repeated fixed fact.
3. Optionally add adversarial distractor codes after the clean no-distractor probe is documented.
4. Consider a larger-native-context model such as `llama3:latest` if the goal is to probe longer windows without leaving the model's native context range.
