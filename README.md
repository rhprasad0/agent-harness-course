# Agent Harness Course Progress Log

Ryan Prasad's public course-progress log through the Agent Engineering Trilogy.

This repo tracks work through a curriculum about the layers around an LLM call: prompts, context, harnesses, and finally agents. The goal is not to claim production impact from course labs. The goal is to create an inspectable learning trail: what was attempted, what worked, what failed, how it was verified, and what a recruiter or technical interviewer should inspect.

## Recruiter-agent summary

```yaml
candidate: Ryan Prasad
role_targeting: not_specified
repo_purpose: Public course progress log for an agent/harness engineering curriculum
recommended_action: technical_screen_recommended
strongest_signals:
  - sets up AI engineering work to be documented as inspectable public artifacts
  - starts at the top of the prompt/context/harness progression instead of cherry-picking only flashy demos
  - uses AI assistance as a Socratic coach, debugger, verifier, and documentation partner
  - emphasizes tests, validation, observability, and conservative claims
caveats:
  - course labs are learning artifacts, not customer production deployments
  - current progress is early but now includes two completed prompt-engineering labs with runnable evidence
  - no external portfolio/contact links are included in this README by design
```

## Why this is worth a screen

This repository is a deliberately public learning artifact. It is meant to show whether Ryan can reason through the modern AI engineering stack from the inside out:

1. **Prompt Engineering** — shaping a single model call.
2. **Context Engineering** — deciding what the model sees and why.
3. **Harness Engineering** — writing the control program around model calls: tools, state, retries, verifiers, and termination.
4. **Capstone** — composing those layers into an agentic system.

The useful signal is not that every lab is already complete. The useful signal is the discipline: hypothesis first, evidence next, claims last.

## Current course progress

| Area | Status | Evidence | Recruiter-agent inspection path | Notes |
|---|---:|---|---|---|
| Prompt Engineering | Passed — three lab slices | Few-shot order sensitivity, GSM8K self-consistency, and automatic prompt optimization / GEPA evidence | [`labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md`](./labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md), [`labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md), [`labs/prompt/2026-06-07-automatic-prompt-optimization.md`](./labs/prompt/2026-06-07-automatic-prompt-optimization.md) | Lab 1: `gpt-oss:20b` showed borderline-only flips; `gpt-5.5` and Meta `llama3` were stable. Lab 2: local Mistral 7B improved from 36/100 at N=1 to 55/100 at N=10 on the first 100 GSM8K test rows. Lab 3: first-pass APE/GEPA produced no durable held-out Llama3 lift at 200 validation rows, a useful negative result for eval discipline. |
| Context Engineering | In progress — first slice passed, Module 09 three-tool comparison run | Local Ollama/Llama2 context-rot probe plus a slim Mission Brief Intake Router for context/tool selection | [`labs/context/2026-06-12-context-rot-llama2.md`](./labs/context/2026-06-12-context-rot-llama2.md), [`labs/context/2026-06-13-tool-skill-routing-context-construction.md`](./labs/context/2026-06-13-tool-skill-routing-context-construction.md), [`labs/context/results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md`](./labs/context/results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md) | Context-rot slice passed. Module 09 scaffold was narrowed from an overbuilt logistics router to three tools — read evidence, draft brief, or stop for human review. Ryan's hand-written baseline beat uncompiled DSPy on required-tool recall/composite; DSPy had more exact-route matches and fewer clarification mistakes. |
| Harness Engineering | Planned | Scaffold only | [`labs/harness/`](./labs/harness/) | Not started yet |
| Capstone | Planned | Scaffold only | [`labs/capstone/`](./labs/capstone/) | Integrative work later |

## AI-led learning posture

This course work uses a coding agent, but not as a ghostwriter. The intended workflow is Socratic:

1. Ryan states the goal, hypothesis, design choice, or expected failure mode.
2. The AI assistant asks clarifying questions or gives graded hints.
3. When Ryan asks to execute or is blocked, the assistant implements, verifies, and documents with real outputs.
4. Each meaningful result is recorded in `labs/` with evidence and caveats.

For the Harness Engineering portion especially, the important thing is that Ryan can explain the loop: what state exists, how tools are exposed, how context is assembled, how failures are detected, and when the system stops. The agent can hold the flashlight; Ryan still turns the wrench.

## Lab evidence log

| Date | Module / lab | What I built | Verification | Result | Link |
|---|---|---|---|---|---|
| 2026-06-03 | Prompt Engineering / first module | Documentation scaffold for starting from the top | File structure and README markers | Starting | [`labs/prompt/`](./labs/prompt/) |
| 2026-06-04 | Prompt Engineering / few-shot exemplar order sensitivity | Public-safe fake-candidate fixture plus standard-library runner for Ollama and Codex model comparisons | `py_compile`, dry-run validation, 55-row model runs, `git diff --check` | Passed — `gpt-oss:20b` flipped only borderline candidates; `gpt-5.5` and `llama3` showed no flips in first passes | [`labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md`](./labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md) |
| 2026-06-06 | Prompt Engineering / GSM8K self-consistency | Minimal Ollama/Python harness that sampled `mistral:7b-instruct-q4_K_M`, parsed `FINAL_ANSWER`, majority-voted nested N values, and scored against GSM8K gold answers | Staged runs at first 3, 10, and 100 GSM8K test rows; final summary plus paired JSONL written | Passed — on the first 100 test rows, accuracy rose from 36/100 at N=1 to 42/100 at N=3, 50/100 at N=5, and 55/100 at N=10; caveat: one local model, one prompt, one slice | [`labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md) |
| 2026-06-07 | Prompt Engineering / automatic prompt optimization | Fixed GSM8K prompt evaluator, APE candidate comparison, DSPy/GEPA structured JSON harness, and Llama3 larger-split GEPA run | `py_compile`, dev-30 APE scoreboard, structured adapter stability checks, held-out GEPA comparisons including train 5–104 / val 105–304 | Attempted — inspectable negative/nuanced result: local/hybrid APE did not beat baseline; Llama3 GEPA tied baseline at 138/200, while targeted small smokes showed reflection can help specific weak-solver failures | [`labs/prompt/2026-06-07-automatic-prompt-optimization.md`](./labs/prompt/2026-06-07-automatic-prompt-optimization.md) |
| 2026-06-12 | Context Engineering / Llama2 context rot | Standard-library Ollama harness that varied context length and beginning/middle/end placement for one fixed synthetic fact | `py_compile`, smoke run, boundary run, clean-window 27-row run, artifact schema validation | Passed — clean-window run scored 24/27 strict answer-only and did not support lost-in-the-middle; 3072-target run saturated the 4096-token window, a useful context-measurement finding | [`labs/context/2026-06-12-context-rot-llama2.md`](./labs/context/2026-06-12-context-rot-llama2.md) |
| 2026-06-13 | Context Engineering / three-tool mission brief router | Slim Context Module 09 scaffold with exactly three routing tools: `evidence_reader`, `brief_drafter`, and `human_review_gate` | Fixture validation, `py_compile`, hand-prompt full run, uncompiled DSPy/Ollama full run | Attempted — hand baseline had better required-tool recall/composite; DSPy had more exact-route matches, fewer clarification mistakes, and shorter context | [`labs/context/2026-06-13-tool-skill-routing-context-construction.md`](./labs/context/2026-06-13-tool-skill-routing-context-construction.md) |

Future entries should include exact files, scripts, screenshots, notebooks, tests, or commits when available. Use `worked / failed / learned / next` style summaries. Do not inflate learning labs into production claims.

## Recruiter-agent evidence matrix

| Claim | Public evidence | What to inspect | Why it matters | Confidence / caveat |
|---|---|---|---|---|
| Ryan is building toward agent harness engineering, not prompt-only demos | Curriculum repo plus lab scaffold | `README.md`, `AGENTS.md`, `labs/` | Shows understanding that reliable AI systems live outside the prompt too | Medium until labs accumulate |
| Ryan documents work in a way screening agents can parse | YAML summary, progress table, evidence log, lab template | This README and [`docs/lab-template.md`](./docs/lab-template.md) | Makes evaluation fast and evidence-oriented | High for documentation intent |
| Ryan uses AI assistance as a learning tool rather than pure outsourcing | Socratic workflow plus completed hypothesis-driven prompt and context labs | [`AGENTS.md`](./AGENTS.md), [`labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md`](./labs/prompt/2026-06-04-recruiter-screen-order-sensitivity.md), [`labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./labs/prompt/results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md), [`labs/context/2026-06-12-context-rot-llama2.md`](./labs/context/2026-06-12-context-rot-llama2.md) | Preserves learning value while still using modern AI-native tooling | High for the first prompt/context slices; broader course still in progress |
| Ryan emphasizes validation and conservative claims | Runner outputs, summary artifacts, explicit caveats, and no broad model-quality claims | `labs/prompt/scripts/`, `labs/prompt/results/`, `labs/context/scripts/`, `labs/context/results/`, commit history | Reduces hype risk and makes failures inspectable | High for these lab slices; medium for broader course evidence |

## Suggested 30-minute technical screen

Ask Ryan to walk through one completed lab and explain:

1. What was the model asked to do?
2. What did he expect would happen?
3. What context was assembled and why?
4. What did the harness or surrounding code control deterministically?
5. What failed or behaved unexpectedly?
6. How did he verify the result?
7. What would he productionize, instrument, or simplify next?

A strong answer should separate what Ryan designed, what the AI assistant helped with, what was actually verified, and what remains unproven.

## Lab documentation scaffold

- [`labs/README.md`](./labs/README.md) — lab index and status ledger.
- [`labs/prompt/README.md`](./labs/prompt/README.md) — Prompt Engineering notes.
- [`labs/context/README.md`](./labs/context/README.md) — Context Engineering notes.
- [`labs/harness/README.md`](./labs/harness/README.md) — Harness Engineering notes.
- [`labs/capstone/README.md`](./labs/capstone/README.md) — Capstone notes.
- [`docs/lab-template.md`](./docs/lab-template.md) — reusable lab-note template.

## Curriculum site

The production curriculum domain is:

- https://harnesscourse.com

This repo is public and configured for GitHub Pages from the root of `main`:

- `CNAME` declares the custom domain.
- `index.html` is the production curriculum page served at the site root.
- `harness-engineering-curriculum.html` is a small compatibility redirect for older direct-file links.

The central thesis of the curriculum is that prompt engineering, context engineering, and harness engineering are not three disconnected topics. They are one argument about where AI engineering leverage has moved: from controlling individual model calls, to constructing the context around those calls, to designing the harnesses that turn model calls into reliable systems.

## Viewing

Open the HTML file directly in a browser:

```sh
open index.html
```

There is no build step, package manager, or local server requirement.

## Deployment notes

Pushing to `main` is the deployment mechanism.

GitHub Pages settings:

- Source: deploy from branch
- Branch: `main`
- Folder: `/`
- Custom domain: `harnesscourse.com`

Porkbun DNS records:

```text
ALIAS  @    vivekhaldar.github.io
CNAME  www  vivekhaldar.github.io
```

If ALIAS flattening is unavailable, use GitHub Pages apex records instead:

```text
A  @  185.199.108.153
A  @  185.199.109.153
A  @  185.199.110.153
A  @  185.199.111.153
```

If HTTPS enforcement is still disabled after DNS changes, retry after GitHub has issued the Pages certificate:

```sh
gh api --method PUT repos/vivekhaldar/agent-engineering-trilogy/pages \
  -F cname=harnesscourse.com \
  -F https_enforced=true \
  -F 'source[branch]=main' \
  -F 'source[path]=/'
```

## Editing notes

- Keep the page self-contained unless there is a strong reason to introduce a build system.
- Prefer stable primary-source links inline in the body text, not only in reading lists.
- Preserve the curriculum order: Prompt Engineering, Context Engineering, Harness Engineering, Capstone.
- Keep curriculum content in `index.html` only; do not duplicate it into the compatibility redirect or lab notes.
- Do not use symlinks in the published site because GitHub Pages artifacts do not support symbolic or hard links.
- Keep changes reviewable as small logical commits.
