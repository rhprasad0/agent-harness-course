# Plan: Minimal GSM8K Self-Consistency Harness for Ollama

## Goal

Build a minimal, repeatable harness that tests whether inference-time sampling plus majority voting improves GSM8K accuracy for a local Ollama model.

The core lab question:

> When a weaker local model has a noisy distribution over reasoning traces, can a harness improve final numeric answers by sampling multiple completions and voting?

This is a harness-engineering lab, not a claim that the model “knows math.” The artifact should make the accuracy-vs-cost curve visible and public-safe.

## Current context / assumptions

- Repository: `/home/ryan/projects/agent-harness-course`
- Current branch state before this plan: `main` is locally ahead of origin; previous GSM8K calibration work was committed locally in `7130a21 feat: add GSM8K local model calibration artifacts`.
- Existing dataset path: `labs/prompt/data/gsm8k/test.jsonl`
- Existing manifest path: `labs/prompt/data/gsm8k/manifest.json`
- Existing deterministic eval script: `labs/prompt/scripts/run_gsm8k_ollama_eval.py`
- Existing model calibration results:
  - `mistral:7b-instruct-q4_K_M`: 35/100 on first 100 GSM8K test questions at temperature 0.
  - `llama2:7b-chat-q4_0`: 24/100 on first 100 GSM8K test questions at temperature 0.
- Preferred teaching model for this harness: `mistral:7b-instruct-q4_K_M`.
- The initial self-consistency hypothesis is intentionally uncertain:
  - `N=5` may show mixed movement with modest net gain.
  - Larger `N` values may improve accuracy if correct reasoning paths are sampled often enough.
  - If the curve is flat or worse, that is still a valid lab finding.

## Experiments already tried

### GSM8K data download and validation

Input artifact:

- OpenAI Grade School Math / GSM8K JSONL files downloaded under `labs/prompt/data/gsm8k/`.

Result status: Passed.

Recorded manifest includes source URLs, byte sizes, row counts, SHA256 hashes, schema checks, and final-answer marker validation.

What this proved:

- The repo has a local public-safe benchmark with deterministic numeric labels.
- The harness does not need API data access or private data.

### GPT-OSS smoke test

Command shape:

```bash
python3 labs/prompt/scripts/run_gsm8k_ollama_eval.py \
  --data labs/prompt/data/gsm8k/train.jsonl \
  --limit 10 \
  --model gpt-oss:20b \
  --temperature 0 \
  --num-predict 512
```

Result status: Passed as smoke test, but not suitable as lab model.

Signal:

- 10/10 correct on first 10 GSM8K training questions.
- Artifact paths:
  - `labs/prompt/results/2026-06-06T144852Z-gsm8k-train-first10-ollama-gpt-oss-smoke.jsonl`
  - `labs/prompt/results/2026-06-06T144852Z-gsm8k-train-first10-ollama-gpt-oss-smoke-summary.md`

What this proved:

- Local Ollama calls worked.
- The first-10 training slice was too easy and not a useful self-consistency demo.
- GPT-OSS should be ignored for this lab’s first self-consistency harness.

### Local weak-model calibration

Command shape:

```bash
python3 labs/prompt/scripts/run_gsm8k_ollama_eval.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --limit 100 \
  --model mistral:7b-instruct-q4_K_M \
  --temperature 0 \
  --num-predict 512

python3 labs/prompt/scripts/run_gsm8k_ollama_eval.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --limit 100 \
  --model llama2:7b-chat-q4_0 \
  --temperature 0 \
  --num-predict 512
```

Result status: Passed.

Signals:

| Model | Correct | Accuracy | Avg sec/q | Avg completion tokens |
|---|---:|---:|---:|---:|
| `mistral:7b-instruct-q4_K_M` | 35/100 | 35.0% | 1.53s | 178.1 |
| `llama2:7b-chat-q4_0` | 24/100 | 24.0% | 1.37s | 163.6 |

Artifact paths:

- `labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval.jsonl`
- `labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval-summary.md`
- `labs/prompt/results/2026-06-06T153015Z-gsm8k-test-first100-ollama-llama2-7b-chat-q4_0-eval.jsonl`
- `labs/prompt/results/2026-06-06T153015Z-gsm8k-test-first100-ollama-llama2-7b-chat-q4_0-eval-summary.md`

What this proved:

- Mistral is likely the better first teaching model: weak enough to leave room for improvement, not so weak that voting is obviously hopeless.
- Llama2 is useful as an older weak comparison, but probably not the first self-consistency target.

## Proposed approach

Create a single Python harness that:

1. Loads the first `limit` GSM8K test rows.
2. Builds one consistent reasoning prompt per question.
3. Calls Ollama repeatedly at a sampling temperature.
4. Generates `max(N)` samples once per question.
5. Computes majority-vote results over nested prefixes such as `N=1`, `N=5`, `N=10`, and `N=20`.
6. Scores voted answers against normalized GSM8K gold answers.
7. Writes:
   - detailed JSONL result records,
   - a Markdown summary table,
   - conservative notes about scope and limitations.

The nested-prefix design is important:

```text
Generate 20 samples once:
N=1  => samples[0:1]
N=5  => samples[0:5]
N=10 => samples[0:10]
N=20 => samples[0:20]
```

This reduces randomness in the curve and makes the question precise:

> Did adding samples 2–5, 6–10, or 11–20 improve the vote?

## Step-by-step implementation plan

### 1. Create the self-consistency script

Add:

```text
labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py
```

Core CLI arguments:

```text
--data             default labs/prompt/data/gsm8k/test.jsonl
--model            default mistral:7b-instruct-q4_K_M
--base-url         default http://127.0.0.1:11434
--limit            default 100
--temperature      default 0.7
--n-values         default 1,5,10,20
--num-predict      default 512
--results-dir      default labs/prompt/results
--seed             optional metadata only unless sampling order is later randomized
```

Do not add dependencies beyond the Python standard library.

### 2. Reuse minimal functions from the deterministic eval script

Reuse or copy these concepts from `labs/prompt/scripts/run_gsm8k_ollama_eval.py`:

- `load_rows(path, limit)`
- `gold_answer(answer)`
- `normalize_numeric(text)`
- `extract_model_answer(text)`
- `ollama_generate(...)`
- `build_prompt(question)`

Possible refactor later:

- Extract shared helper functions into `labs/prompt/scripts/gsm8k_ollama_common.py`.

For v0, keep one standalone script if that is faster and clearer. Avoid over-architecting the raccoon cage.

### 3. Implement sample generation

For each question:

```python
max_n = max(n_values)
samples = []
for sample_index in range(1, max_n + 1):
    response = ollama_generate(...)
    pred_raw = extract_model_answer(response_text)
    pred_norm = normalize_numeric(pred_raw)
    samples.append({...})
```

Each sample record should include:

```json
{
  "sample_index": 1,
  "pred_raw": "18",
  "pred_norm": "18",
  "sample_correct": true,
  "elapsed_seconds": 1.23,
  "ollama_eval_count": 180,
  "ollama_prompt_eval_count": 70,
  "ollama_total_duration_ns": 1234567890,
  "error": null,
  "model_response": "..."
}
```

### 4. Implement majority voting over nested prefixes

For each requested `N`:

```python
prefix = samples[:N]
voted_answer, tie = majority_vote(prefix)
vote_correct = voted_answer == gold_norm
```

Tie policy:

- Count normalized predictions with `Counter`.
- If more than one answer has the top count, choose the tied answer that appeared earliest in the prefix.
- Record `tie=true` so the result is not hidden.

Parse failure policy:

- If a sample has no parseable numeric answer, set `pred_norm = null`.
- Exclude `null` from voting if at least one parsed answer exists.
- If all prefix samples are unparseable, set `voted_answer = null`, `vote_correct = false`, and increment parse-failure statistics.

### 5. Write JSONL result artifact

One JSONL row per GSM8K question.

Suggested schema:

```json
{
  "index": 1,
  "question": "...",
  "gold_raw": "18",
  "gold_norm": "18",
  "model": "mistral:7b-instruct-q4_K_M",
  "temperature": 0.7,
  "n_values": [1, 5, 10, 20],
  "samples": [...],
  "votes": {
    "1": {
      "voted_answer": "18",
      "vote_correct": true,
      "tie": false,
      "parsed_sample_count": 1,
      "parse_failure_count": 0
    },
    "5": {
      "voted_answer": "18",
      "vote_correct": true,
      "tie": false,
      "parsed_sample_count": 5,
      "parse_failure_count": 0
    }
  }
}
```

Result filename pattern:

```text
labs/prompt/results/<timestamp>-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency.jsonl
```

### 6. Write Markdown summary artifact

Suggested summary path:

```text
labs/prompt/results/<timestamp>-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md
```

Required report fields:

- Date/time
- Model
- Dataset path
- Slice definition
- Temperature
- N values
- Number of questions
- Generation budget
- Table by N:

```text
| N | Correct | Accuracy | Rescued vs N=1 | Broken vs N=1 | Ties | All-parse-fail votes | Avg sec/q | Avg completion tokens/q |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
```

Definitions:

- `Rescued vs N=1`: N=1 vote wrong, N=k vote correct.
- `Broken vs N=1`: N=1 vote correct, N=k vote wrong.
- `Ties`: number of questions where a tie existed for that N prefix.
- `All-parse-fail votes`: number of questions where all samples in the prefix failed numeric parsing.
- `Avg sec/q`: average total generation time per question for the prefix size.
- `Avg completion tokens/q`: average sum of Ollama completion tokens per question for the prefix size.

Add a short interpretation section with conservative language:

- `Passed`: harness ran and produced artifacts.
- `Inconclusive`: if accuracy movement is too small or noisy.
- Avoid broad claims from first-100 only.

### 7. Add optional deterministic baseline comparison in the summary

Do not rerun the deterministic eval inside this v0 script unless necessary.

Instead, optionally reference the existing deterministic Mistral artifact:

```text
labs/prompt/results/2026-06-06T152742Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-eval-summary.md
```

The summary can compare:

- deterministic `temp=0, N=1`: 35/100
- sampled `temp=0.7, N=1`: measured by this harness
- sampled `temp=0.7, N=5/10/20`: measured by this harness

This distinction matters:

- deterministic baseline answers “how good is one boring call?”
- sampled N=1 answers “what does a single draw from the sample distribution look like?”
- N>1 answers “does voting over draws help?”

### 8. Add one smoke mode before full run

Before the 100-question run, execute a tiny smoke run during implementation:

```bash
python3 labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --model mistral:7b-instruct-q4_K_M \
  --limit 3 \
  --temperature 0.7 \
  --n-values 1,3 \
  --num-predict 256
```

Expected validation:

- Script exits 0.
- JSONL and Markdown files are written.
- Each JSONL row has exactly 3 samples.
- Summary includes N=1 and N=3 rows.
- Parse failures, if any, are recorded rather than crashing.

### 9. Run the first real self-consistency experiment

Initial full command:

```bash
python3 labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --model mistral:7b-instruct-q4_K_M \
  --limit 100 \
  --temperature 0.7 \
  --n-values 1,5,10,20 \
  --num-predict 512
```

Expected runtime estimate:

- Prior deterministic Mistral was about 1.53s/question for one call.
- This run requires 20 calls/question × 100 questions = 2,000 calls.
- Rough estimate: 45–70 minutes, depending on sampling speed and token lengths.
- If that is too slow, first run `--limit 25` or `--n-values 1,5,10` as an intermediate calibration.

### 10. Document the result as lab evidence

After the harness run succeeds, add or update a lab note using the repo lab style.

Likely files:

```text
labs/prompt/README.md
labs/prompt/<new-or-existing-self-consistency-lab-note>.md
```

If no lab note exists yet for this module, create one from:

```text
docs/lab-template.md
```

The lab note should include:

- Objective
- Hypothesis
- Harness design
- Model and dataset details
- Command run
- Result table
- Evidence artifact paths
- Failure/surprise notes
- Next step

Keep claims conservative: first-100 slice, one model, one prompt, one temperature.

## Files likely to change

Primary implementation:

```text
labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py
```

Likely generated artifacts:

```text
labs/prompt/results/<timestamp>-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency.jsonl
labs/prompt/results/<timestamp>-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md
```

Possible documentation updates after execution:

```text
labs/prompt/README.md
labs/prompt/<self-consistency-lab-note>.md
```

Possible future refactor, not required for v0:

```text
labs/prompt/scripts/gsm8k_ollama_common.py
```

## Tests / validation

### Static checks

```bash
python3 -m py_compile labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py
git diff --check
```

### Dataset/manifest check

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('labs/prompt/data/gsm8k')
manifest = json.loads((base / 'manifest.json').read_text())
for filename, item in manifest['files'].items():
    path = base / filename
    rows = sum(1 for _ in path.open(encoding='utf-8'))
    assert rows == item['rows'], (path, rows, item['rows'])
print('gsm8k manifest row counts ok')
PY
```

### Smoke run

```bash
python3 labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --model mistral:7b-instruct-q4_K_M \
  --limit 3 \
  --temperature 0.7 \
  --n-values 1,3 \
  --num-predict 256
```

Then verify output structure:

```bash
python3 - <<'PY'
import json
from pathlib import Path
paths = sorted(Path('labs/prompt/results').glob('*self-consistency.jsonl'))
latest = paths[-1]
rows = [json.loads(line) for line in latest.read_text().splitlines()]
assert len(rows) == 3
for row in rows:
    assert len(row['samples']) == 3
    assert '1' in row['votes'] and '3' in row['votes']
print(f'smoke artifact ok: {latest}')
PY
```

### Full run

```bash
python3 labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py \
  --data labs/prompt/data/gsm8k/test.jsonl \
  --model mistral:7b-instruct-q4_K_M \
  --limit 100 \
  --temperature 0.7 \
  --n-values 1,5,10,20 \
  --num-predict 512
```

Then verify:

```bash
python3 - <<'PY'
import json
from pathlib import Path
paths = sorted(Path('labs/prompt/results').glob('*mistral*first100*self-consistency.jsonl'))
latest = paths[-1]
rows = [json.loads(line) for line in latest.read_text().splitlines()]
assert len(rows) == 100
for row in rows:
    assert len(row['samples']) == 20
    for n in ['1', '5', '10', '20']:
        assert n in row['votes']
print(f'full artifact ok: {latest}')
PY
```

### Repo-specific verification before commit

For content/data/script changes:

```bash
git diff --check
if rg -n "TODO|FIXME|Google search|Graduate Curriculum" index.html; then
  echo "Review the matches above before committing."
  exit 1
else
  echo "content scan ok"
fi
test "$(cat CNAME)" = "harnesscourse.com"
python3 -m py_compile labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py
```

If lab docs are updated, also run:

```bash
rg -n "Course Progress Log|Lab evidence log|Recruiter-agent|AI-led lab workflow|Socratic" README.md AGENTS.md labs docs
```

### Public-safety scan

Run before commit:

```bash
rg -n "api[_-]?key|token|secret|password|bearer|authorization|sk-[A-Za-z0-9]" \
  labs/prompt/scripts \
  labs/prompt/results \
  labs/prompt/*.md \
  docs || true
```

Expected caveat:

- GSM8K itself contains ordinary words like “token” and “secret” in math word problems. Those are not credentials.
- Public-safety review should focus on generated harness artifacts and scripts, not false-positive math story text.

## Risks, tradeoffs, and open questions

### Runtime cost

`N=20` over 100 questions means 2,000 local generations. This is feasible but may take close to an hour.

Mitigation:

- Smoke with `limit=3`.
- Optional intermediate run: `limit=25`, `n-values=1,5,10`.
- Use foreground for short smoke, background with completion notification for full run.

### Prompt sensitivity

A single prompt may understate or overstate the model’s self-consistency behavior.

Mitigation:

- Treat this as a first harness slice.
- Do not claim prompt-general results.
- If needed later, add prompt variants as a separate controlled experiment.

### Majority vote can amplify wrong modes

If the model often samples the same wrong answer, voting can make the wrong answer more stable.

Mitigation:

- Report rescued and broken cases.
- Report answer-distribution examples.
- Include “all samples wrong” / “dominant wrong answer” observations in lab notes if visible.

### Tie handling can affect scores

Even N values can tie. First-seen tie-breaking is deterministic but arbitrary.

Mitigation:

- Record tie counts.
- Consider a later sensitivity pass that marks ties wrong or inconclusive.

### Parser artifacts

Fallback-to-last-number can accidentally score an answer that was not intended as the final answer.

Mitigation:

- Prefer `FINAL_ANSWER` marker.
- Record raw model responses.
- Report parse failure counts and parsing policy.
- If parsing looks flaky, improve prompt/parser before trusting the curve.

### Open question: include Llama2 in first self-consistency run?

Recommended answer for v0: no.

Use Mistral first because calibration places it closer to the useful band. Llama2 can be a later comparison if the Mistral curve is interesting or if the lab wants to show failure modes.

### Open question: should the first 100 test questions be replaced by a seeded random subset?

Recommended answer for v0: keep first 100 for continuity with existing calibration artifacts.

Future improvement:

- Add `--sample-size` and `--seed` for pre-registered random slices.
- Record selected indices in the result artifact.

## Commit plan after execution

If implementation and validation pass, commit only intended files:

```bash
git status --short --ignored
git add \
  labs/prompt/scripts/run_gsm8k_self_consistency_ollama.py \
  labs/prompt/results/<self-consistency-jsonl> \
  labs/prompt/results/<self-consistency-summary-md> \
  labs/prompt/README.md \
  labs/prompt/<self-consistency-lab-note>.md

git diff --cached --check
git diff --cached --name-status
git commit -m "feat: add GSM8K self-consistency harness"
```

Do not push unless Ryan explicitly asks to push.

## Success criteria

The plan is complete when execution produces:

1. A working standalone Python self-consistency harness.
2. A smoke run with valid JSONL and Markdown artifacts.
3. A 100-question Mistral run with nested N results for `1,5,10,20`.
4. A summary table showing accuracy, rescued/broken counts, ties, parse failures, time, and tokens.
5. Conservative lab documentation or at least result artifacts suitable for a later lab note.

Tiny gym whistle: if the curve is ugly, the harness still wins. Ugly curves are data wearing sweatpants.
