# Plan: Context Rot Lab Harness with Ollama Llama2

## Goal

Design and implement the first Context Engineering lab evidence slice: a small-scale context-rot / lost-in-the-middle experiment using `llama2` on Ollama.

The curriculum task from `index.html:1255-1270` is:

> Replicate a small-scale context-rot experiment on a model the students can call, plotting accuracy vs. context length on a fixed task.

Ryan's current hypothesis is **B — lost-in-the-middle**:

> The answer-bearing fact placed in the middle of longer contexts will degrade sooner than the same fact placed near the beginning or end.

Ryan selected **A — one hidden fact repeated across all trials** for the first pass. This keeps the lab simple and debuggable. The caveat is that repeated trials are not evidence of broad fact-retrieval skill; they are a controlled probe of length/position behavior on one fixed retrieval task.

## Current context / assumptions

- Repo root: `/home/ryan/projects/agent-harness-course`
- Context lab status is currently **Planned** in `labs/context/README.md`.
- The lab should be public-safe and recruiter-readable.
- Production curriculum remains in `index.html`; lab evidence belongs under `labs/context/`.
- No framework or package manager should be added unless necessary.
- Prefer standard-library Python where possible.
- Ollama is available locally: `ollama version is 0.30.4`.
- Target model is installed as `llama2:7b-chat-q4_0` (`ollama list` ID `78e26419b446`, size `3.8 GB`). Use this exact tag in the harness and lab note rather than the ambiguous alias `llama2`.
- GPU is an RTX 3090 with 24,576 MiB VRAM; preflight showed about 21,311 MiB free before loading the model.
- A one-call Ollama sanity check with `num_ctx=4096` loaded `llama2:7b-chat-q4_0` as `100% GPU`, `CONTEXT 4096`, and returned `Mango-orbit-92` for the fixed-token prompt.
- Research finding: Ollama can allocate larger context by VRAM tier, and current docs say 24-48 GiB VRAM defaults to 32k context, but Meta Llama 2 itself is a 4k-context model. For this lab, keep `num_ctx=4096` to avoid turning the experiment into unsupported RoPE/context-extension behavior.
- Because plan mode is active, this file is only the execution plan; no harness code or experiments have been run in this turn.

## Experiments already tried

### Ollama/model preflight

Commands:

```sh
ollama list
ollama --version
nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv,noheader,nounits
curl -s http://localhost:11434/api/generate \
  -d '{"model":"llama2:7b-chat-q4_0","prompt":"Return only this token: mango-orbit-92","stream":false,"options":{"temperature":0,"num_predict":32,"num_ctx":4096}}'
ollama ps
```

Observed signals:

- Installed models include `llama2:7b-chat-q4_0`, `llama3:latest`, `mistral:7b-instruct-q4_K_M`, and `gpt-oss:20b`.
- `llama2:7b-chat-q4_0` is installed and callable.
- GPU: `NVIDIA GeForce RTX 3090, 24576 MiB total, 21311 MiB free` before the model sanity check.
- Sanity response was `Mango-orbit-92`; normalization should handle case differences.
- `ollama ps` after the call showed `llama2:7b-chat-q4_0` loaded at `100% GPU` with `CONTEXT 4096`.

What this proved:

- Open question 1 is resolved: use `llama2:7b-chat-q4_0`.
- The model can run fully on GPU at `num_ctx=4096`.
- The harness should record the exact model tag and `ollama ps` context value in the lab note.

### Context-length research

Findings:

- Ollama documentation defines context length as the maximum tokens the model has access to and says larger context increases required memory. It also documents VRAM-tier defaults: `<24 GiB = 4k`, `24-48 GiB = 32k`, `>=48 GiB = 256k`.
- The Meta Llama 2 model card/paper lists Llama 2 7B/13B/70B with **4k context length**.
- Therefore, the clean lab should use `num_ctx=4096` for Llama2. Going above 4096 would test context extension/extrapolation and truncation behavior, not the base model's native long-context behavior.

Resolved decision:

- Use `num_ctx=4096` for v1.
- Adjust length ladder from word-heavy `500,2000,4000` to a token-aware ladder that stays inside the 4096-token native window after prompt overhead. Recommended v1 ladder: approximately `512,1536,3072` target context tokens, implemented using generated filler units and validated with Ollama's `prompt_eval_count`.

### Execution update

After implementation, the `3072` target context setting produced `prompt_eval_count=4095` for every long row, meaning it saturated Llama2's 4096-token native context window. A follow-up clean-window run used `512,1536,2300` target context tokens instead. The clean-window run produced observed average prompt eval counts around 793, 2194, and 3255 tokens and scored 24/27 strict answer-only. It did **not** support the lost-in-the-middle hypothesis: the middle placement scored 3/3 at the long setting, while beginning scored 1/3 and end scored 2/3 because of extra-text answer-format failures.

Final documentation artifacts:

- `labs/context/scripts/run_context_rot_ollama.py`
- `labs/context/2026-06-12-context-rot-llama2.md`
- `labs/context/results/2026-06-12T140307Z-context-rot-llama2-summary.md` for the boundary run
- `labs/context/results/2026-06-12T140407Z-context-rot-llama2-summary.md` for the clean-window run

## Experiment design

### Fixed task

Use one hidden synthetic fact throughout the first pass.

Candidate fixed fact:

```text
Project Lantern access code is mango-orbit-92.
```

Question:

```text
What is the Project Lantern access code? Answer with only the access code.
```

Expected answer:

```text
mango-orbit-92
```

This value is synthetic, public-safe, and easy to exact-match.

### Variables

1. **Context length**
   - Target context sizes should be token-aware and validated with Ollama's `prompt_eval_count`.
   - Initial staged ladder for native Llama 2 context:
     - `short`: ~512 target context tokens
     - `medium`: ~1,536 target context tokens
     - `long`: ~3,072 target context tokens
   - Do **not** include an 8k-context v1 run with Llama 2; Meta's Llama 2 context length is 4k, so 8k would confound context rot with context extension/truncation behavior.

2. **Needle position**
   - `beginning`
   - `middle`
   - `end`

3. **Repeats**
   - Start with `3` repeats per `(length, position)` cell for a quick smoke/full first pass.
   - If runtime is acceptable and failures are interesting, scale to `5` or `10` repeats later.

### Constants

- Same model: `llama2:7b-chat-q4_0`
- Same question
- Same hidden fact
- Same output contract: answer only the access code
- Same generation settings for all cells:
  - `temperature=0.0`
  - fixed `num_predict`, likely `32` or `64`
  - fixed Ollama options including `num_ctx=4096`
- Same scoring rule:
  - Normalize whitespace and common quote/punctuation wrappers.
  - Exact-match the expected access code.
  - Anything else is incorrect, with failure type classified.

## Proposed harness shape

### New script

Create:

```text
labs/context/scripts/run_context_rot_ollama.py
```

Responsibilities:

1. Generate synthetic distractor text deterministically.
2. Insert the fixed fact at beginning/middle/end.
3. Call Ollama's local HTTP API for each trial.
4. Record one JSONL row per trial.
5. Write a compact Markdown summary table grouped by context length and needle position.
6. Optionally write a CSV summary for plotting.

Use Python standard library only:

- `argparse`
- `csv`
- `datetime`
- `json`
- `random`
- `statistics`
- `time`
- `urllib.request`
- `urllib.error`
- `hashlib`
- `pathlib`

Avoid introducing dependencies for v1. If plotting is needed later, create a CSV first and optionally add a simple SVG/Markdown table rather than requiring matplotlib.

### Candidate CLI

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

Optional larger run if smoke passes should increase repeats, not context beyond Llama 2's native window:

```sh
python3 labs/context/scripts/run_context_rot_ollama.py \
  --model llama2:7b-chat-q4_0 \
  --target-tokens 512,1536,3072 \
  --positions beginning,middle,end \
  --repeats 10 \
  --temperature 0 \
  --num-predict 64 \
  --num-ctx 4096 \
  --out-dir labs/context/results
```

### Output artifacts

Use timestamped filenames:

```text
labs/context/results/YYYY-MM-DDTHHMMSSZ-context-rot-llama2.jsonl
labs/context/results/YYYY-MM-DDTHHMMSSZ-context-rot-llama2-summary.csv
labs/context/results/YYYY-MM-DDTHHMMSSZ-context-rot-llama2-summary.md
```

JSONL row schema:

```json
{
  "run_id": "YYYY-MM-DDTHHMMSSZ",
  "model": "llama2:7b-chat-q4_0",
  "trial_id": "long-middle-002",
  "length_label": "long",
  "target_context_tokens": 3072,
  "prompt_eval_count": 3250,
  "position": "middle",
  "needle_offset_units": 42,
  "question": "What is the Project Lantern access code? Answer with only the access code.",
  "expected_answer": "mango-orbit-92",
  "raw_response": "mango-orbit-92",
  "normalized_response": "mango-orbit-92",
  "correct": true,
  "failure_type": "correct",
  "elapsed_seconds": 1.234,
  "prompt_sha256": "...",
  "prompt_chars": 12345,
  "response_chars": 14,
  "ollama_done_reason": "stop",
  "error": null
}
```

Failure taxonomy:

- `correct`
- `wrong_fact`
- `missing_answer`
- `extra_text`
- `format_error`
- `timeout`
- `ollama_error`
- `setup_error`

The harness should preserve raw responses because failure examples are the most useful teaching evidence.

## Prompt template

Keep the prompt boring and invariant:

```text
You are given a context document and a question.
Answer the question using only the context document.
Return only the exact access code. Do not explain.

Context document:
---
{context}
---

Question: What is the Project Lantern access code?
Answer:
```

The hidden fact should appear as a plain sentence inside the context:

```text
Project Lantern access code is mango-orbit-92.
```

Distractor text should include plausible but non-conflicting filler. For v1, avoid adversarial fake access codes so the first result isolates length/position rather than distractor confusion. A later v2 can add adversarial distractors.

## Step-by-step execution plan

### Phase 1 — Preflight discovery

1. Check current repo status:

   ```sh
   git status --short
   git branch --show-current
   ```

2. Verify Ollama and model availability:

   ```sh
   ollama list
   ```

3. Record resolved model tag: `llama2:7b-chat-q4_0`.

4. Run a one-call manual sanity check before building a large batch:

   ```sh
   curl -s http://localhost:11434/api/generate \
     -d '{"model":"llama2:7b-chat-q4_0","prompt":"Return only this token: mango-orbit-92","stream":false,"options":{"temperature":0,"num_predict":32,"num_ctx":4096}}'
   ```

Record setup blockers separately from model failures.

### Phase 2 — Implement harness

1. Create `labs/context/scripts/run_context_rot_ollama.py`.
2. Implement deterministic distractor generation with a fixed seed.
3. Implement context assembly for beginning/middle/end placement.
4. Implement Ollama API call with JSON response parsing and timeout handling.
5. Implement answer normalization and failure classification.
6. Implement JSONL, CSV, and Markdown summary outputs.
7. Add `--dry-run` or `--preview-only` if useful to inspect generated prompt sizes without calling the model.

### Phase 3 — Smoke test

Run the smallest useful test:

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

Smoke success criteria:

- Script exits 0.
- JSONL exists and has 3 rows.
- Markdown summary exists.
- No setup errors.
- At least one row returns a parseable response.

If all rows fail due to output format, first tighten the prompt or parser before scaling.

### Phase 4 — First real run

Run the first evidence slice:

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

Interpretation rules:

- If middle fails more than beginning/end at longer lengths, mark as evidence consistent with the lost-in-the-middle hypothesis.
- If all positions fail early, report model/task mismatch or context-window/setup issue, not context rot.
- If all positions pass, report no observed rot at this scale and propose increasing length or adding distractors.
- If only end fails, investigate truncation or prompt construction before making claims.

### Phase 5 — Documentation updates

Create lab note:

```text
labs/context/2026-06-12-context-rot-llama2.md
```

Use `docs/lab-template.md` sections:

- Metadata
- Objective
- Hypothesis / expected failure mode
- Socratic prompts / hints used
- Attempt
- Verification
- Result
- Recruiter-agent inspection notes
- Next step

Update context lab index:

```text
labs/context/README.md
```

If the first run produces real evidence, update:

```text
labs/README.md
README.md
```

Keep statuses conservative:

- `Starting` if only harness/scaffold exists.
- `Attempted` if the harness ran but results are blocked/inconclusive.
- `Passed — first context-rot slice` only if the run completes and artifacts support a clear result or clear negative finding.

## Files likely to change

New files:

```text
labs/context/scripts/run_context_rot_ollama.py
labs/context/results/<timestamp>-context-rot-llama2.jsonl
labs/context/results/<timestamp>-context-rot-llama2-summary.csv
labs/context/results/<timestamp>-context-rot-llama2-summary.md
labs/context/2026-06-12-context-rot-llama2.md
```

Modified files after evidence exists:

```text
labs/context/README.md
labs/README.md
README.md
```

Do not modify `index.html` for this lab unless the curriculum itself needs correction.

## Tests / validation

### Script validation

```sh
python3 -m py_compile labs/context/scripts/run_context_rot_ollama.py
```

### Artifact validation

```sh
test -s labs/context/results/<run_id>-context-rot-llama2.jsonl
test -s labs/context/results/<run_id>-context-rot-llama2-summary.md
python3 - <<'PY'
import json
from pathlib import Path
path = Path('labs/context/results/<run_id>-context-rot-llama2.jsonl')
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
assert rows, 'no rows'
required = {'run_id','model','length_label','position','expected_answer','raw_response','correct','failure_type'}
for i, row in enumerate(rows, 1):
    missing = required - row.keys()
    assert not missing, f'row {i} missing {missing}'
print(f'validated {len(rows)} rows')
PY
```

### Repo documentation validation

For content-only/doc edits, run the repo checks from `AGENTS.md`:

```sh
git diff --check
if rg -n "TODO|FIXME|Google search|Graduate Curriculum" index.html; then
  echo "Review the matches above before committing."
  exit 1
else
  echo "content scan ok"
fi
test "$(cat CNAME)" = "harnesscourse.com"
```

For lab documentation updates, also run:

```sh
rg -n "Course Progress Log|Lab evidence log|Recruiter-agent|AI-led lab workflow|Socratic" README.md AGENTS.md labs docs
```

## Risks and tradeoffs

1. **Single hidden fact is easy to debug but weak evidence**
   - Good for v1 harness validation.
   - Caveat clearly in the lab note.
   - Follow-up v2 should use different facts per trial.

2. **Llama2 may have limited effective context**
   - If `xl` contexts fail due to truncation or local context settings, record as setup/model-capacity finding.
   - Do not claim context rot when the prompt was not actually inside the model's context window.

3. **Exact output contract may be brittle**
   - That brittleness is part of the harness finding if it grows with length.
   - But if all failures are extra prose, consider parser normalization before interpreting as retrieval failure.

4. **Repeated same fact may create pattern learning within the run?**
   - Ollama calls are stateless, so no conversational memory should carry over.
   - Still, repeated identical answer means this is not a broad benchmark.

5. **Approximate token counts**
   - Standard-library v1 may measure words/chars rather than true tokenizer tokens.
   - Label as approximate unless a tokenizer dependency is added later.

## Resolved decisions

1. Use the installed exact Ollama tag: `llama2:7b-chat-q4_0`.
2. Use `num_ctx=4096` for v1 because Llama 2's native context length is 4k tokens, even though the RTX 3090/Ollama runtime may be able to allocate more VRAM-backed context.
3. Do not include an 8k-context first run for Llama 2. Use a native-window ladder around `512,1536,3072` target context tokens and validate each row's `prompt_eval_count`.
4. Do not add adversarial fake access codes in v1. Keep this as a pure length/position probe; add distractor codes later only if the clean run is too easy or inconclusive.

## Recommended first execution default

Use a conservative staged run:

1. Smoke: `512` target context tokens × 3 positions × 1 repeat.
2. First evidence slice: `512,1536,3072` target context tokens × 3 positions × 3 repeats.
3. If the first evidence slice is too clean, increase repeats or move to a v2 model with a larger native context; do not silently push Llama 2 beyond 4k and call it the same experiment.

This keeps the lab from becoming a GPU space heater with a clipboard.
