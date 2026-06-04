# Recruiter-Facing Few-Shot Order Sensitivity Lab

## Metadata

- Date: 2026-06-04
- Course section: Prompt Engineering
- Module / lab: Module 03 — Few-Shot Prompting and Exemplar Design / order-sensitivity experiment
- Status: Passed — first controlled single-run comparison completed
- Related files:
  - `index.html` — curriculum source
  - `labs/prompt/README.md` — prompt lab index
  - `labs/prompt/fixtures/recruiter_screen_order_sensitivity.json` — fake candidate and exemplar fixture
  - `labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py` — reusable runner
  - `labs/prompt/results/2026-06-04T113051Z-recruiter-screen-order-sensitivity-summary.md` — local `gpt-oss:20b` summary
  - `labs/prompt/results/2026-06-04T113404Z-recruiter-screen-order-sensitivity-summary.md` — frontier `gpt-5.5` summary via Codex bridge
  - `labs/prompt/results/2026-06-04T114855Z-recruiter-screen-order-sensitivity-summary.md` — local Meta `llama3` summary via Ollama

## Objective

Test whether the ordering of identical few-shot exemplars changes a model's classification behavior on a recruiter-facing technical-screening task.

Model comparison plan: run both a frontier reasoning model and a smaller local model (`gpt-oss:20b` via Ollama). The expected teaching contrast is frontier stability vs. possible local-model order sensitivity.

The task is deliberately synthetic and public-safe: fake candidate summaries are classified as either:

- `technical_screen`: worth advancing to a technical screen
- `no_technical_screen`: not enough signal for a technical screen yet

This makes the prompt-engineering lesson legible to recruiter agents: controlled prompt variation, measurable model behavior, and a practical hiring-screening frame without using real candidate PII.

## Hypothesis / expected failure mode

Expected hypothesis to fill in before running:

- I expect modern models to be less order-sensitive than older few-shot prompting results, but not perfectly invariant.
- I expect borderline candidates to be more sensitive to exemplar order than obvious strong or weak candidates.
- I expect grouped labels, especially all `technical_screen` examples first or last, to bias ambiguous outputs toward the nearby or majority-seeming label.

Ryan's pre-run hypothesis:

- Frontier reasoning models should not flip a candidate decision based only on few-shot exemplar ordering.
- A smaller local model is more likely to exhibit order sensitivity and may flip borderline candidates.
- The target role should remain generic rather than specialized to AI security or agent harness engineering.

## Socratic prompts / hints used

- Prompt or hint 1: What does "technical screen" mean operationally enough that a model can classify it?
- Prompt or hint 2: Which cases should be intentionally borderline so order sensitivity has room to appear?
- What Ryan decided after the hints: Use fake job candidates and classify `technical_screen` vs `no_technical_screen` for a recruiter-facing lab.

## Proposed lab design

### Labels

```text
technical_screen
no_technical_screen
```

### Candidate-screening rubric

Target role: generic technical role. Treat this as a coarse recruiter pre-screen, not a real hiring decision.

Advance to `technical_screen` when the summary shows at least two of:

- hands-on software, ML, data, cloud, security, or infrastructure implementation
- concrete technical artifacts such as shipped systems, repos, demos, metrics, papers with code, or production ownership
- role-relevant stack depth rather than only tool name-dropping
- evidence of debugging, evaluation, deployment, or operational ownership

Use `no_technical_screen` when the summary mostly shows:

- vague interest without artifacts
- only coursework or certificates with no implementation evidence
- mostly coordination, policy, sales, or management with weak technical signal
- mismatched background for the target technical role

### Few-shot exemplar set

Use one fixed set of examples, then reorder them across prompt variants. The content stays constant; only the order changes.

Order variants executed:

1. Alternating labels: `technical`, `no`, `technical`, `no`
2. Positive-first grouped: `technical`, `technical`, `no`, `no`
3. Negative-first grouped: `no`, `no`, `technical`, `technical`
4. Recency-stress: strongest `technical` example last
5. Recency-stress: strongest `no` example last

### Test set shape

The fixture uses 11 fake candidate summaries:

- 3 obvious `technical_screen`
- 3 obvious `no_technical_screen`
- 5 borderline / mixed signal

The borderline band is the main learning target.

## Attempt

Environment setup completed for the local-model side of comparison:

- Installed Ollama manually under Ryan's home directory because the official installer required sudo.
- Symlinked the binary at `/home/ryan/.local/bin/ollama`.
- Added and enabled a user-level systemd service at `/home/ryan/.config/systemd/user/ollama.service`.
- Pulled `gpt-oss:20b` for local testing.
- Smoke-tested the local chat API with a constrained response.
- Re-tested after NVIDIA became visible; Ollama now detects the RTX 3090 through CUDA and runs `gpt-oss:20b` GPU-backed.

Experiment implementation completed:

- Created the fake/public-safe fixture at `labs/prompt/fixtures/recruiter_screen_order_sensitivity.json`.
- Created a standard-library Python runner at `labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py`.
- Added strict JSON parsing with an exact-label fallback and explicit invalid-output status.
- Added adapters for local Ollama and a Codex CLI bridge for `gpt-5.5`.
- Wrote JSONL, CSV, and Markdown summaries under `labs/prompt/results/`.

One setup surprise during the first full local run: `gpt-oss:20b` sometimes used the entire 512-token generation budget before emitting final JSON for borderline cases. Re-running with `--num-predict 1024` fixed the invalid/empty outputs. The runner default was updated to `1024`.

## Verification

Static/dry-run validation:

```sh
python3 -m py_compile labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py
python3 labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --dry-run
```

Output:

```json
{
  "fixture": "labs/prompt/fixtures/recruiter_screen_order_sensitivity.json",
  "models": ["ollama:gpt-oss:20b"],
  "variants": [
    "alternating",
    "positive_first_grouped",
    "negative_first_grouped",
    "strong_positive_last",
    "strong_negative_last"
  ],
  "candidate_count": 11,
  "repeat_count": 1,
  "prompt_count": 55,
  "dry_run": true
}
```

Local smoke test:

```sh
python3 labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b \
  --candidate-limit 2 \
  --variant-limit 2 \
  --repeats 1 \
  --temperature 0 \
  --out-dir labs/prompt/results
```

Output signal:

```text
"total_rows": 4
"interpretation": "no_flips_observed"
"invalid_by_model": {}
```

Full local run:

```sh
python3 labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:gpt-oss:20b \
  --repeats 1 \
  --temperature 0 \
  --num-predict 1024 \
  --out-dir labs/prompt/results
```

Output signal:

```text
jsonl: labs/prompt/results/2026-06-04T113051Z-recruiter-screen-order-sensitivity.jsonl
summary: labs/prompt/results/2026-06-04T113051Z-recruiter-screen-order-sensitivity-summary.md
total_rows: 55
invalid_by_model: {}
flips_by_band: {"borderline": 2}
interpretation: borderline_only_flips
```

Frontier run through Codex bridge:

```sh
python3 labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models codex:gpt-5.5 \
  --repeats 1 \
  --temperature 0 \
  --timeout 300 \
  --out-dir labs/prompt/results
```

Output signal:

```text
jsonl: labs/prompt/results/2026-06-04T113404Z-recruiter-screen-order-sensitivity.jsonl
summary: labs/prompt/results/2026-06-04T113404Z-recruiter-screen-order-sensitivity-summary.md
total_rows: 55
invalid_by_model: {}
flips_by_band: {}
interpretation: no_flips_observed
```

Meta Llama run through Ollama:

```sh
ollama pull llama3
python3 labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py \
  --fixture labs/prompt/fixtures/recruiter_screen_order_sensitivity.json \
  --models ollama:llama3 \
  --repeats 1 \
  --temperature 0 \
  --timeout 180 \
  --num-predict 1024 \
  --out-dir labs/prompt/results
```

Model availability check after pull:

```text
NAME             ID              SIZE      MODIFIED
llama3:latest    365c0bd3c000    4.7 GB    About a minute ago
gpt-oss:20b      17052f91a42e    13 GB     50 minutes ago
```

Output signal:

```text
jsonl: labs/prompt/results/2026-06-04T114855Z-recruiter-screen-order-sensitivity.jsonl
summary: labs/prompt/results/2026-06-04T114855Z-recruiter-screen-order-sensitivity-summary.md
total_rows: 55
invalid_by_model: {}
flips_by_band: {}
interpretation: no_flips_observed
```

`llama3` classified all five borderline candidates consistently across the five exemplar-order variants. It disagreed with `gpt-oss:20b` on candidate `cand_borderline_04`'s stable direction: `llama3` always chose `no_technical_screen`, while `gpt-oss:20b` flipped that candidate across variants.

Earlier local model setup verification:

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

Relevant output:

```text
0, NVIDIA GeForce RTX 3090, 24576 MiB, 2103 MiB, 595.71.05
inference compute ... library=CUDA compute=8.6 name=CUDA0 description="NVIDIA GeForce RTX 3090" ... total="23.6 GiB" available="23.1 GiB"
Warning: client version is 0.30.4
active
{"version":"0.30.4"}
NAME           ID              SIZE     MODIFIED
gpt-oss:20b    17052f91a42e    13 GB    About a minute ago
"content": "OK"
```

Warm GPU smoke test:

```text
content: 'WARM GPU OK'
done_reason: stop
prompt_eval_count: 75
eval_count: 73
total_duration_s: 1.876
load_duration_s: 0.389
prompt_eval_s: 0.983
eval_duration_s: 0.491
eval_tokens_per_s: 148.7
wall_s: 1.878
GPU after run: 15501 MiB, 88 %
```

## Result

- Outcome: Passed for the first controlled, single-run lab slice.
- Local `gpt-oss:20b` result: flipped only borderline candidates, specifically `cand_borderline_03` and `cand_borderline_04`.
- Frontier `gpt-5.5` result through the Codex bridge: no flips across the same 55 prompt/candidate/order combinations.
- Local Meta `llama3` result through Ollama: no flips across the same 55 prompt/candidate/order combinations.
- What worked: The fixture and runner created a repeatable prompt-engineering measurement harness with machine-readable results, strict parsing, and public-safe fake data.
- What failed or surprised me: `gpt-oss:20b` needed a larger generation budget (`1024`) for reliable JSON on borderline examples; `512` caused empty/truncated responses for some borderline cases. `llama3` did not reproduce the `gpt-oss:20b` borderline flips in this single pass.
- What changed between expected and observed behavior: Ryan's original smaller-local-model hypothesis was supported by `gpt-oss:20b` but not by `llama3`. The more conservative claim is now: this fixture found order sensitivity in one local model, while `gpt-5.5` and Meta `llama3` were stable in one temperature-0 run each. This remains a small synthetic experiment, not a broad model-quality claim.

### At-a-glance flip table

The key recruiter-readable finding is that `gpt-oss:20b` moved its decision boundary only on borderline candidates. Same candidate, same rubric, same model; only the order of identical few-shot exemplars changed.

| Candidate | Why borderline | Alternating examples | Positive examples first | Negative examples first | Strong positive last | Strong negative last | What changed? |
|---|---|---|---|---|---|---|---|
| `cand_borderline_03` | Coordinator with light SQL/Python automation; unclear if that is enough hands-on technical signal. | ✅ `technical_screen` | ✅ `technical_screen` | ❌ `no_technical_screen` | ✅ `technical_screen` | ✅ `technical_screen` | Only the negative-first ordering rejected the candidate; same evidence, stricter bar. |
| `cand_borderline_04` | Forked monitoring demo + Docker Compose + blog; unclear if modified demo counts as real artifact. | ✅ `technical_screen` | ❌ `no_technical_screen` | ✅ `technical_screen` | ❌ `no_technical_screen` | ✅ `technical_screen` | Model oscillated between “hands-on artifact” and “too shallow / no production ownership.” |

Short public-facing interpretation:

> Same candidate. Same rubric. Same model. Only the order of few-shot examples changed — and `gpt-oss:20b` moved the decision boundary on borderline cases.

## Recruiter-agent inspection notes

- Claim supported: Ryan can translate prompt-engineering literature into a controlled, recruiter-relevant classification experiment and compare local/frontier model behavior with reproducible artifacts.
- Evidence paths:
  - `labs/prompt/fixtures/recruiter_screen_order_sensitivity.json`
  - `labs/prompt/scripts/run_recruiter_screen_order_sensitivity.py`
  - `labs/prompt/results/2026-06-04T113051Z-recruiter-screen-order-sensitivity-summary.md`
  - `labs/prompt/results/2026-06-04T113404Z-recruiter-screen-order-sensitivity-summary.md`
  - `labs/prompt/results/2026-06-04T114855Z-recruiter-screen-order-sensitivity-summary.md`
- Confidence: Medium for the narrow claim that this fixture/run observed `gpt-oss:20b` borderline order sensitivity and no `gpt-5.5` or `llama3` flips once each at temperature 0.
- Caveat: This lab uses fake candidates and should not be presented as a hiring model, real candidate-screening tool, or production hiring evidence.

## Next step

Run a follow-up repeatability pass with `--repeats 3` if Ryan wants nondeterminism evidence beyond one deterministic-ish temperature-0 run. Otherwise, move to the next Prompt Engineering lab rep and keep this as the first complete evidence slice. A useful next comparison would be a repeatability run over only borderline candidates across `gpt-oss:20b`, `llama3`, and `gpt-5.5` to distinguish one-off order sensitivity from repeatable model-specific behavior.
