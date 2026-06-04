# Plan: Candidate fixture and runner for recruiter-screen order-sensitivity lab

## Goal

Build the next executable slice of the Prompt Engineering lab: a public-safe fake-candidate fixture plus a runner that compares exemplar-order sensitivity across:

- Frontier model path: Codex bridge using `gpt-5.5`.
- Local model path: Ollama `gpt-oss:20b` on the RTX 3090.

The output should be a repeatable lab artifact that records classifications, parses model responses into the fixed label set, summarizes order flips, and updates the existing lab note conservatively.

## Current context / assumptions

- Repo: `/home/ryan/projects/agent-harness-course`.
- Existing lab note: `labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md`.
- Existing lab index: `labs/prompt/README.md`.
- The lab is intentionally fake/public-safe and should not use real candidate PII.
- The target role remains generic technical role, not AI security / agent harness specialist.
- Labels are already defined:
  - `technical_screen`
  - `no_technical_screen`
- Planned prompt-order variants are already documented:
  1. Alternating labels: `technical`, `no`, `technical`, `no`
  2. Positive-first grouped: `technical`, `technical`, `no`, `no`
  3. Negative-first grouped: `no`, `no`, `technical`, `technical`
  4. Recency-stress: strongest `technical` example last
  5. Recency-stress: strongest `no` example last
- Ollama `gpt-oss:20b` has already been smoke-tested GPU-backed on RTX 3090, with warm generation around 148.7 eval tokens/sec.
- Plan mode is active: this file is a plan only. Do not implement until Ryan explicitly asks to execute.

## Experiments already tried

### Environment/setup success: local Ollama path

Input artifact / command shape:

```sh
nvidia-smi --query-gpu=index,name,memory.total,memory.used,driver_version --format=csv,noheader
journalctl --user -u ollama.service -n 120 --no-pager | grep 'inference compute'
/home/ryan/.local/bin/ollama --version
systemctl --user is-active ollama.service
curl -fsS http://127.0.0.1:11434/api/version
/home/ryan/.local/bin/ollama list
curl -fsS http://127.0.0.1:11434/api/chat \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK."}],"stream":false,"options":{"num_predict":128,"temperature":0}}'
```

Result status: success.

Exact success signals recorded in the lab note:

```text
0, NVIDIA GeForce RTX 3090, 24576 MiB, 2103 MiB, 595.71.05
inference compute ... library=CUDA compute=8.6 name=CUDA0 description="NVIDIA GeForce RTX 3090" ... total="23.6 GiB" available="23.1 GiB"
active
{"version":"0.30.4"}
gpt-oss:20b    17052f91a42e    13 GB
"content": "OK"
```

Warm GPU smoke test signal:

```text
content: 'WARM GPU OK'
total_duration_s: 1.876
eval_tokens_per_s: 148.7
GPU after run: 15501 MiB, 88 %
```

What this proves:

- Local model execution is available and GPU-backed.
- The remaining blocker is experiment implementation and result collection, not GPU/model installation.
- `gpt-oss:20b` may require enough `num_predict` budget because it can spend early output in hidden/thinking fields before final content.

### Environment/setup caveat: Ollama install path

Result status: compatibility workaround.

Observed issue:

- Official Ollama installer required sudo.

Workaround:

- User-local install at `/home/ryan/.local/bin/ollama`.
- User-level systemd service at `/home/ryan/.config/systemd/user/ollama.service`.

What this proves:

- Future scripts should not assume `/usr/bin/ollama`.
- The runner should call Ollama over `http://127.0.0.1:11434/api/chat` rather than shelling out to a hardcoded binary.

## Proposed approach

Create a small, reviewable Python runner with data separated from code:

1. Fixture defines examples, candidate cases, expected band, and prompt-order variants.
2. Runner renders the same task prompt for every `(model, order_variant, candidate)` combination.
3. Runner calls two model adapters:
   - `ollama_chat` for `gpt-oss:20b` via local HTTP.
   - `codex_bridge` for `gpt-5.5` via Codex CLI or a small bridge wrapper.
4. Runner requires strict JSON output with a label and short rationale.
5. Runner robustly extracts/validates labels and marks invalid responses explicitly instead of pretending they succeeded.
6. Results are written to timestamped JSONL/CSV artifacts under `labs/prompt/results/`.
7. A summary command computes label flips by candidate and model across order variants.
8. Lab docs are updated with real result evidence after the run.

## Files likely to change

Create:

- `labs/prompt/fixtures/recruiter_screen_order_sensitivity.json`
  - Public-safe fake exemplar and candidate data.
- `labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py`
  - Main runner.
- `labs/prompt/results/.gitkeep`
  - Keeps output directory present without committing large/generated result batches.

Generated during execution:

- `labs/prompt/results/YYYY-MM-DDTHHMMSSZ-recruiter-screen-order-sensitivity.jsonl`
- `labs/prompt/results/YYYY-MM-DDTHHMMSSZ-recruiter-screen-order-sensitivity-summary.csv`
- Optional: `labs/prompt/results/YYYY-MM-DDTHHMMSSZ-recruiter-screen-order-sensitivity-summary.md`

Update after execution:

- `labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md`
  - Add implementation details, command, result table, flip summary, caveats.
- `labs/prompt/README.md`
  - Move status from `Attempted` to `Passed`, `Inconclusive`, or `Failed` depending on result quality.

Optional if the repo prefers documented command entrypoints:

- `labs/prompt/scripts/README.md`
  - Explain model prerequisites and runner usage.

## Candidate fixture design

### Exemplar set

Use four fixed few-shot examples, intentionally balanced:

1. Strong `technical_screen`
   - Hands-on implementation, concrete artifacts, debugging/evaluation signal.
2. Moderate `technical_screen`
   - Stack depth and shipped/demo evidence, not superstar language.
3. Clear `no_technical_screen`
   - Vague interest, certificates/coursework, no implementation evidence.
4. Clear `no_technical_screen`
   - Coordination/policy/management-heavy, weak hands-on technical signal.

Each exemplar should include:

```json
{
  "id": "ex_pos_strong_01",
  "label": "technical_screen",
  "strength": "strong",
  "summary": "...fake candidate summary...",
  "rationale": "...why this label follows the rubric..."
}
```

### Test candidates

Use 8–12 fake candidates across three bands:

- Obvious strong: 2–3 candidates.
- Obvious weak: 2–3 candidates.
- Borderline/mixed: 4–6 candidates.

Each test candidate should include:

```json
{
  "id": "cand_borderline_01",
  "band": "borderline",
  "summary": "...fake candidate summary...",
  "expected_stability": "possibly_unstable",
  "notes": "...human expectation, not model truth..."
}
```

Important safety/content rules:

- No real names, emails, companies, schools, phone numbers, locations, or biographical facts from real people.
- Use generic fake identifiers: `Candidate A`, `Candidate B`, or `cand_borderline_01`.
- Make this a prompt-engineering measurement harness, not a hiring recommendation system.

## Prompt design

The rendered prompt should include:

1. System/developer framing:
   - This is a synthetic prompt-engineering lab.
   - Classify fake summaries for a generic technical pre-screen.
   - Return only JSON.
2. Rubric copied from the lab note.
3. Few-shot examples in the selected order.
4. One candidate summary.
5. Strict output schema:

```json
{
  "label": "technical_screen | no_technical_screen",
  "confidence": "low | medium | high",
  "rationale": "one sentence, no private data"
}
```

Parsing rule:

- Primary parse: JSON object.
- Fallback parse: exact label token search only if JSON parse fails.
- If neither works, record `parsed_label = null`, `parse_status = "invalid_response"`, and preserve a truncated raw response for debugging.

## Runner design

### CLI shape

Primary command:

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b,codex:gpt-5.5 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Fast local-only development command:

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b \
  --candidate-limit 2 \
  --variant-limit 2 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

### Output schema per JSONL row

```json
{
  "run_id": "2026-06-04T072127Z",
  "model_adapter": "ollama",
  "model": "gpt-oss:20b",
  "candidate_id": "cand_borderline_01",
  "candidate_band": "borderline",
  "order_variant": "positive_first_grouped",
  "repeat": 1,
  "temperature": 0,
  "prompt_sha256": "...",
  "raw_response_truncated": "...",
  "parsed_label": "technical_screen",
  "confidence": "medium",
  "parse_status": "json_ok",
  "latency_seconds": 1.23,
  "usage": {
    "prompt_eval_count": 123,
    "eval_count": 45
  },
  "error": null
}
```

### Summary metrics

The script should compute and print/save:

- Total calls attempted/succeeded/failed by model.
- Invalid response count by model.
- For each candidate/model:
  - labels observed across variants.
  - `flip_count` or `is_order_sensitive` boolean.
- Flip rate by candidate band:
  - obvious strong.
  - obvious weak.
  - borderline.
- A conservative interpretation helper:
  - `no_flips_observed`
  - `borderline_only_flips`
  - `invalid_outputs_prevent_claim`
  - `broad_instability_observed`

## Codex bridge plan for `gpt-5.5`

Preferred implementation sequence:

1. Keep Codex bridge isolated behind a model adapter interface so local-only runs work without Codex.
2. For each prompt, invoke Codex in one-shot mode with a strict instruction to return only the JSON classification object.
3. Use `pty=true` when Hermes executes Codex directly, per Codex CLI requirements.
4. Use an output capture option if available in installed Codex CLI, such as `--output-last-message <tmpfile>`, to reduce terminal-control noise.
5. If direct per-candidate Codex CLI calls are too slow/noisy, implement a `--frontier-input-jsonl` mode that writes prompts to JSONL and a separate bridge command processes them in batch.

Candidate command shape for execution phase:

```sh
codex exec \
  --model gpt-5.5 \
  -c 'model_reasoning_effort="xhigh"' \
  --sandbox read-only \
  --output-last-message /tmp/recruiter-screen-codex-response.json \
  '<strict JSON classification prompt>'
```

Fallback if Codex bridge is unreliable:

- Run the local Ollama path first and mark frontier comparison as `blocked_frontier_bridge`.
- Preserve generated prompt artifacts so the same prompt can be manually or later bridge-tested with `gpt-5.5`.
- Do not fabricate frontier results.

## Step-by-step execution plan

1. Inspect current lab note and index.
   - Confirm labels, rubric, hypothesis, and order variants are still aligned.
2. Create fixture directory and fixture file.
   - `labs/prompt/fixtures/recruiter_screen_order_sensitivity.json`.
   - Include schema version, labels, rubric summary, examples, order variants, candidates.
3. Create runner script.
   - `labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py`.
   - Use only Python standard library if possible: `argparse`, `json`, `csv`, `hashlib`, `datetime`, `subprocess`, `urllib.request`, `time`, `pathlib`.
   - Keep model adapters small and testable.
4. Add deterministic dry-run mode.
   - `--dry-run` renders prompts and validates fixture/order variants without calling models.
   - Save prompt preview or print count only; avoid huge output by default.
5. Add local Ollama adapter.
   - POST to `http://127.0.0.1:11434/api/chat`.
   - Use `stream:false`, `temperature:0`, enough `num_predict` such as 256–512.
   - Record Ollama timing/usage fields where present.
6. Add Codex adapter.
   - Shell out to `codex exec` only when `codex:gpt-5.5` is requested.
   - Capture output to temp file when possible.
   - Record command failure as a structured error row.
7. Add parser and validator.
   - JSON parse first.
   - Exact label fallback second.
   - Invalid output remains invalid; no silent coercion.
8. Add summary writer.
   - JSONL raw results.
   - CSV or Markdown summary.
   - Console summary suitable for pasting into the lab note.
9. Run validation in phases.
   - Dry-run fixture validation.
   - Fast local-only smoke: 2 candidates × 2 variants.
   - Full local run.
   - Frontier/Codex run.
   - Combined summary.
10. Update lab docs with exact command and observed result.
    - Preserve conservative status if frontier path blocks or invalid outputs are high.

## Tests / validation

Run these in order during execution.

### Static checks

```sh
python -m py_compile labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --dry-run
```

Expected signal:

- Fixture loads.
- All order variants reference existing exemplar IDs.
- Candidate count and prompt count are printed.
- No model calls are made.

### Local smoke test

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b \
  --candidate-limit 2 \
  --variant-limit 2 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Expected signal:

- 4 result rows.
- `parse_status` is `json_ok` or documented fallback, not mostly invalid.
- Summary file exists.

### Full local run

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Expected signal:

- `candidate_count × 5` result rows for local model.
- Flip summary generated.
- Borderline candidates are specifically visible in the summary.

### Frontier/Codex bridge run

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models codex:gpt-5.5 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Expected signal:

- Frontier rows are recorded or structured `error` rows explain the bridge failure.
- If Codex auth/CLI fails, report that as environment/setup blocked; do not substitute Hermes model outputs.

### Combined run

```sh
python labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b,codex:gpt-5.5 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Expected signal:

- Both adapters represented in JSONL, or a clear partial/blocker status.
- Summary compares local vs frontier without overstating claims.

### Repository checks after docs update

```sh
git diff --check
rg -n "real candidate|actual candidate|production hiring|hiring model|customer impact|PII|email|phone" labs/prompt docs README.md AGENTS.md || true
rg -n "Recruiter-facing few-shot order sensitivity|order sensitivity|gpt-oss:20b|gpt-5.5|technical_screen|no_technical_screen" labs/prompt
```

Expected signal:

- No whitespace errors.
- No accidental real-candidate/production-hiring claims.
- New artifacts are discoverable by expected lab markers.

## Risks, tradeoffs, and open questions

### Risks

- Codex CLI may be slower/noisier than a direct API bridge and may need auth refresh.
- Strict JSON may fail for `gpt-oss:20b`; fallback parser must record invalidity honestly.
- Temperature 0 reduces sampling variance but does not prove general stability.
- One repeat per variant is enough for a first lab slice but not enough for broad model-quality claims.
- Generated result artifacts can grow; keep committed artifacts small and reviewable.

### Tradeoffs

- Standard-library Python keeps the repo lightweight and static-site friendly.
- A fixture JSON file is more verbose than inline script constants but better for course evidence/review.
- Codex bridge allows the requested `gpt-5.5` frontier path, but a true API adapter would be cleaner if Ryan later wants high-volume repeated trials.

### Open questions to resolve during execution

1. Commit generated full result JSONL or only commit a small summary plus raw excerpt?
   - Recommended: commit summary Markdown/CSV and a small representative JSONL, keep large repeated batches untracked if they become bulky.
2. Should repeats stay at 1 for first proof or increase to 3 for nondeterminism evidence?
   - Recommended first execution: `repeats=1`; follow-up: `repeats=3` only if the runner is stable and cost/time is acceptable.
3. Should the lab status become `Passed` if local completes but Codex bridge blocks?
   - Recommended: `Inconclusive` or `Attempted` for comparison; `Passed local-runner slice` only if status language clearly scopes the claim.

## Definition of done

The implementation is done when:

- Fixture exists and contains only fake/public-safe candidate data.
- Runner dry-run validates fixture and prompt counts.
- Ollama local smoke test produces parseable result rows.
- Full local run produces a flip summary.
- Codex `gpt-5.5` bridge either produces comparable rows or a structured, honest blocker artifact.
- Existing lab note records commands, outputs, result status, and caveats.
- Lab index points to the result evidence.
- `git diff --check` passes.
- Public-safety scan does not show accidental real-candidate or production-hiring claims.
