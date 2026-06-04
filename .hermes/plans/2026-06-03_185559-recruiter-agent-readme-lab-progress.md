# Plan: Recruiter-agent README for Ryan's Agent Harness Course lab progress

## Goal

Update `README.md` and `AGENTS.md` so the repo stops reading like only a static curriculum/deployment note and starts functioning as Ryan's public, recruiter-agent-facing course-progress artifact plus an AI-led educational exercise.

The README should answer, quickly and defensibly:

- What is this repo?
- Why is Ryan working through it?
- What labs has he completed or is actively documenting?
- What concrete AI Engineering skills should a recruiter agent inspect?
- What public evidence exists, and what claims are still intentionally conservative?

The AGENTS.md should guide future AI assistants to act as Socratic tutors/coaches for the labs: ask Ryan to form hypotheses, offer graded hints before direct answers, document reasoning and evidence, and preserve the course/product constraints.

This is a planning-only artifact. Do not edit `README.md`, `AGENTS.md`, or scaffold files until Ryan approves or says to execute.

## Current context / assumptions

- Repository path: `/home/ryan/projects/agent-harness-course`
- Current branch status at planning time: `main...origin/main`, clean working tree.
- Current repo files discovered:
  - `README.md`
  - `index.html`
  - `harness-engineering-curriculum.html`
  - `CNAME`
  - `AGENTS.md`
- Repo purpose from `AGENTS.md`: static public curriculum artifact for the Agent Engineering Trilogy.
- Production page: `index.html`; compatibility redirect: `harness-engineering-curriculum.html`.
- Existing README is currently mostly operational/deployment documentation for `harnesscourse.com` and GitHub Pages.
- User intent for this update: document Ryan's work on course labs and make it recruiter-agent-facing.
- Public-safety posture: public artifact is allowed, but do not expose secrets, tokens, PII beyond already-public identity/contact choices, home IPs, registrar/account/billing details, or private notes.
- Career-positioning posture: frame Ryan as an AI Engineering candidate, not a Data Engineer. Emphasize harnesses, agents, evals, context systems, observability, and lab evidence.

## Experiments already tried

### Repo acquisition and baseline verification

- Input artifact: `https://github.com/rhprasad0/agent-harness-course`
- Command shape: `git clone https://github.com/rhprasad0/agent-harness-course.git`
- Result status: success.
- Success signal:
  - Repo cloned to `/home/ryan/projects/agent-harness-course`.
  - Current branch: `main` tracking `origin/main`.
  - Current HEAD observed after clone: `b35d874`.
  - Working tree clean at plan time.
- What this proves: we can safely plan against the local repo and later execute as a normal README/docs edit.

### Read-only repo inspection

- Inspected `README.md`.
- Inspected `AGENTS.md`.
- Listed repo files.
- Searched `index.html` for curriculum/lab structure, headings, and lab-related markers.
- Result status: success.
- What this proved:
  - README has no current Ryan-specific progress/log/evidence section.
  - Existing repo guidance requires keeping curriculum content centralized in `index.html` and treating the HTML as the product.
  - A README update can be done without touching the curriculum page, unless Ryan later wants progress links surfaced on the site itself.

## Resolved decisions

Ryan answered the open planning questions on 2026-06-03:

- Course progress starts from the top of the curriculum.
- First active area: Prompt Engineering, starting from the top / first prompt lab.
- README title/framing: `Course Progress Log`.
- First execution should update `README.md` and add a `labs/` documentation scaffold.
- Do not optimize for specific named target roles in this repo README.
- Do not link additional public artifacts yet.
- Do not add contact info.
- Also update `AGENTS.md` so the repo is framed as an AI-led educational exercise.
- Use the Socratic method for AI assistance: questions and hints first, direct solutions only when asked or needed to unblock.

## Proposed README direction

The README should become a hybrid of:

1. **Project/course wrapper**: preserve what the repo is and where the curriculum lives.
2. **Ryan's course progress log**: show progress through the trilogy with dated lab notes and status.
3. **Recruiter-agent artifact**: provide a structured evidence matrix, recommended screen action, and inspection paths without forcing a role-specific pitch.

It should not pretend the course work is production impact. The strongest framing is:

> Ryan is publicly working through an agent/harness engineering curriculum and documenting implementation labs as inspectable evidence of AI engineering practice. This repo is a learning-and-evidence trail: what was built, what was tested, what failed, and what a recruiter or technical interviewer should inspect.

## Recommended AGENTS.md direction

Keep `AGENTS.md` concise. Do not turn it into a 900-line constitution wearing a fake mustache.

Add or revise a top-level section that says this repo is now both:

1. A static curriculum artifact for the Agent Engineering Trilogy.
2. Ryan's AI-led course-progress workspace for working through labs with an assistant.

The new agent guidance should preserve existing production-site rules while adding an educational operating mode:

### AI-led educational exercise

Future assistants should behave as Socratic lab coaches:

- Start by asking Ryan what he thinks the next step, hypothesis, or failure mode is.
- Prefer questions and graded hints before giving direct answers.
- When Ryan is blocked or explicitly asks for implementation, switch from hinting to execution.
- Explain the principle behind each lab artifact, not just the command that produces it.
- Keep lab notes evidence-backed: objective, hypothesis, attempt, result, failure, next step.
- Let Ryan do as much reasoning as practical; the AI can scaffold, inspect, verify, and document.
- Avoid inventing progress or claiming mastery from placeholders.

### AGENTS.md constraints to preserve

Keep existing guardrails:

- `index.html` remains the production curriculum page.
- `harness-engineering-curriculum.html` remains a redirect only.
- `CNAME` must remain `harnesscourse.com`.
- No framework, package manager, bundler, or generated asset pipeline unless explicitly requested.
- Preserve the curriculum order: Prompt Engineering, Context Engineering, Harness Engineering, Capstone.
- Keep public-safety boundaries around secrets, registrar/account/billing details, and private metadata.

### Suggested AGENTS.md section skeleton

```md
## AI-led lab workflow

This repo is also Ryan's AI-led course-progress workspace. Future agents should act like Socratic lab coaches, not answer vending machines.

Default loop:

1. Ask Ryan to state the goal, hypothesis, or expected failure mode.
2. Offer one or two hints before giving a full solution.
3. When Ryan asks to execute, implement directly and verify with real outputs.
4. Record the lab result in `labs/` using the shared template.
5. Keep claims conservative: mark work as planned, starting, attempted, passed, failed, or inconclusive.

Use direct answers when safety, correctness, or unblocking requires it. Otherwise, make Ryan do the useful thinking reps. Tiny gym whistle optional.
```

## Recommended README structure

### 1. Title and hiring thesis

Replace or expand the top section with:

- `# Agent Harness Course Progress Log`
- Short subtitle: `Ryan Prasad's public course-progress log through the Agent Engineering Trilogy.`
- Above-the-fold thesis:
  - No named role targets in this README.
  - Why this is worth screening: Ryan is not only consuming course content; he is turning labs into public evidence around prompt/context/harness engineering, agent loops, evals, observability, and reliability.
  - Keep the framing broadly AI-engineering-facing rather than role-specific.

### 2. Recruiter-agent quick verdict block

Add a concise agent-readable section:

```yaml
candidate: Ryan Prasad
role_targeting: not_specified
repo_purpose: Public course progress log for an agent/harness engineering curriculum
recommended_action: technical_screen_when_lab_evidence_accumulates
strongest_signals:
  - documents AI engineering work as inspectable public artifacts
  - starts at the top of the prompt/context/harness progression instead of cherry-picking only flashy demos
  - emphasizes tests, validation, observability, and conservative claims
caveats:
  - course labs are learning artifacts, not customer production deployments
  - progress should be evaluated through linked commits, lab notes, and runnable evidence
  - no external portfolio/contact links are included in this README by design
```

Keep this compact and honest. Because Ryan requested no target roles, avoid role lists and instead frame the evidence as generally useful for AI-engineering screening.

### 3. Current course progress

Add a progress table with resolved initial status:

| Area | Status | Evidence | Recruiter-agent inspection path | Notes |
|---|---:|---|---|---|
| Prompt Engineering | Starting | Initial scaffold | `labs/prompt/` | Begin from the first/top prompt module and document from there |
| Context Engineering | Planned | Scaffold only | `labs/context/` | Not started yet |
| Harness Engineering | Planned | Scaffold only | `labs/harness/` | Not started yet |
| Capstone | Planned | Scaffold only | `labs/capstone/` | Integrative work later |

During execution, keep status honest. Do not invent completed labs. The first visible evidence can be the scaffold plus the first prompt-lab note marked `Starting` / `In progress`.

### 4. Lab evidence log

Add a section designed to grow over time:

```md
## Lab evidence log

| Date | Module / lab | What I built | Verification | Result | Link |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | Planned | TBD |
```

Rules for future entries:

- Use dated entries.
- Include exact files, scripts, screenshots, notebooks, tests, or commits when available.
- Use `worked / failed / learned / next` style summaries.
- Do not inflate learning labs into production claims.

### 5. Recruiter-agent evidence matrix

Add a claim/evidence matrix, initially with conservative placeholders if artifacts are not yet created:

| Claim | Public evidence | What to inspect | Why it matters | Confidence / caveat |
|---|---|---|---|---|
| Ryan is building toward agent harness engineering, not prompt-only demos | Curriculum repo + future lab artifacts | README, lab notes, commits | Shows understanding of reliability/control-flow layer | Medium until labs accumulate |
| Ryan documents work in a way agents can parse | This README structure | Tables, YAML block, links | Helps recruiter agents and technical reviewers evaluate quickly | High for documentation intent |
| Ryan emphasizes validation and conservative claims | Future lab logs/tests | Test outputs, failure notes | Reduces hype risk | Medium until evidence exists |

### 6. Suggested technical screen

Add a recruiter/hiring-manager prompt:

```md
## Suggested 30-minute technical screen

Ask Ryan to walk through one completed lab and explain:

1. What was the model asked to do?
2. What context was assembled and why?
3. What did the harness control deterministically?
4. What failed or behaved unexpectedly?
5. How did he verify the result?
6. What would he productionize or instrument next?
```

### 7. Course/site metadata preservation

Keep a shortened version of the existing operational info:

- Production site: `https://harnesscourse.com`
- Main artifact: `index.html`
- Redirect: `harness-engineering-curriculum.html`
- CNAME/GitHub Pages notes
- No build step

Move the current detailed DNS/deployment notes lower in the README so they do not bury Ryan's recruiter-facing progress signal.

## Files likely to change during execution

Primary:

- `AGENTS.md` — update repo-local instructions to include the AI-led Socratic lab workflow while preserving production-site guardrails.
- `README.md`
- `labs/README.md` — index of lab writeups.
- `labs/prompt/README.md` — Prompt Engineering lab notes, starting from the top.
- `labs/context/README.md` — placeholder/scaffold for future Context Engineering labs.
- `labs/harness/README.md` — placeholder/scaffold for future Harness Engineering labs.
- `labs/capstone/README.md` — placeholder/scaffold for future Capstone work.
- `docs/lab-template.md` — reusable lab-note template.

Do not add contact files or role-specific target docs. Keep all scaffold content public-safe and placeholder-honest.

## Step-by-step execution plan

1. **Use the resolved decisions**
   - Start from the top of the curriculum.
   - Mark Prompt Engineering as `Starting` and all later sections as `Planned`.
   - Use `Course Progress Log` framing.
   - Add the `labs/` scaffold and `docs/lab-template.md`.
   - Update `AGENTS.md` with an AI-led Socratic lab workflow.
   - Do not include target roles, outside public artifacts, or contact info.

2. **Draft README rewrite**
   - Preserve factual repo/site metadata.
   - Move recruiter-agent sections near the top.
   - Add progress table, evidence log, evidence matrix, and technical-screen prompt.
   - Keep tone punchy and human, not AI-polished. Avoid corporate oatmeal.

3. **Update AGENTS.md for Socratic AI-led labs**
   - Keep the file concise and durable, following `repo-agent-instructions` guidance.
   - Preserve production-site rules and existing verification commands.
   - Add an `AI-led lab workflow` section that tells future assistants to use the Socratic method: ask for hypotheses, offer hints before full solutions, execute when Ryan asks, and document evidence in `labs/`.
   - Avoid over-prescribing every future lab; AGENTS.md should orient agents, not duplicate this plan.

4. **Create lab documentation scaffold**
   - Create `labs/README.md` as the lab index.
   - Create `labs/prompt/README.md` with the first/top Prompt Engineering lab marked `Starting`.
   - Create `labs/context/README.md`, `labs/harness/README.md`, and `labs/capstone/README.md` as future placeholders.
   - Create `docs/lab-template.md` with reusable fields: date, module, objective, hypothesis, Socratic prompts/hints used, setup, artifact paths, verification, results, failure notes, next step, recruiter-agent inspection notes.

5. **Public-safety review**
   - Check for secrets, tokens, private IPs, registrar/account/billing details, contact info, and overclaim phrases.
   - Do not add personal contact details or external public artifacts.

6. **Validation**
   - Run repo-required checks from `AGENTS.md` after editing:
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
   - Add README-specific checks:
     ```sh
     rg -n "recommended_action: technical_screen_when_lab_evidence_accumulates|Recruiter-agent|Lab evidence log|Suggested 30-minute technical screen|Course Progress Log" README.md
     rg -n "AI-led lab workflow|Socratic|hypothesis|hints before|labs/" AGENTS.md
     test -f labs/README.md
     test -f labs/prompt/README.md
     test -f labs/context/README.md
     test -f labs/harness/README.md
     test -f labs/capstone/README.md
     test -f docs/lab-template.md
     rg -n "secret|token|password|192\.168|10\.|172\.16|Porkbun.*order|billing|mailto:|@" README.md labs docs || true
     ```
   - If links are added, verify they resolve where practical.

7. **Optional read-only recruiter-agent review**
   - Use one read-only subagent or manual review prompt before commit:
     ```text
     You are reviewing a public README intended for FAANG-style recruiter agents screening Ryan Prasad for AI Engineering roles. Use only public evidence in the README and linked public repos. Evaluate whether the README supports a defensible recommendation to move Ryan to technical screen. Check for overclaiming, missing caveats, unclear evidence, poor agent parsability, weak recruiter narrative, and missing inspection paths. Return: pass/fail, top fixes, overclaiming risks, strongest recruiter-agent summary sentence, and whether recommended_action: technical_screen is justified.
     ```

8. **Commit only after Ryan approval**
   - Stage by name:
     ```sh
     git add AGENTS.md README.md labs/README.md labs/prompt/README.md labs/context/README.md labs/harness/README.md labs/capstone/README.md docs/lab-template.md
     ```
   - Suggested commit message:
     ```sh
     git commit -m "docs: frame course progress and AI-led labs"
     ```
   - Push only if Ryan explicitly wants remote publication in the execution request.

## Tests / validation checklist

- `AGENTS.md` includes:
  - Project framed as both a static curriculum artifact and Ryan's AI-led lab workspace.
  - A concise `AI-led lab workflow` section.
  - Socratic method guidance: ask for hypothesis/expected failure, offer hints before full answers, switch to direct execution when Ryan asks or is blocked.
  - Instruction to document lab outcomes in `labs/` using the template.
  - Existing production-site guardrails preserved.
- `README.md` includes:
  - `Course Progress Log` title/framing.
  - `recommended_action: technical_screen_when_lab_evidence_accumulates` in a machine-readable summary block.
  - No named target-role optimization.
  - No contact information.
  - No added external artifact links.
  - Progress table for Prompt, Context, Harness, Capstone.
  - Lab evidence log.
  - Recruiter-agent evidence matrix.
  - Suggested 30-minute technical screen.
  - Clear caveat that course labs are public learning/evidence artifacts, not proof of private production impact.
- Scaffold exists:
  - `labs/README.md`
  - `labs/prompt/README.md`
  - `labs/context/README.md`
  - `labs/harness/README.md`
  - `labs/capstone/README.md`
  - `docs/lab-template.md`
- Existing repo constraints still satisfied:
  - `CNAME` unchanged and exactly `harnesscourse.com`.
  - No build system added.
  - `index.html` remains the curriculum source of truth.
- Public-safety checks pass.
- README does not frame Ryan as a Data Engineer.

## Risks and tradeoffs

- **Risk: overclaiming.** Recruiter-facing does not mean hype-facing. Keep claims evidence-backed.
- **Risk: Socratic mode blocks momentum.** AGENTS.md should say Socratic by default, but direct execution when Ryan asks, safety requires it, or he is blocked. We are building reps, not a riddle dungeon.
- **Risk: AGENTS.md gets too bloated.** Keep the Socratic workflow compact and preserve the existing production-site rules.
- **Risk: README becomes too long.** Use headings and tables; keep the top high-signal.
- **Risk: initial progress is thin.** That is acceptable. Mark Prompt Engineering as `Starting`, later sections as `Planned`, and let the scaffold create clean slots for evidence as work happens.
- **Risk: duplicating curriculum content.** Do not summarize every module in README; link to `index.html` / production site and focus on Ryan's lab evidence.
- **Tradeoff: scaffold before artifacts.** Creating `labs/` now adds a little upfront structure, but it prevents the work from turning into a README junk drawer. Tiny bureaucracy, but the useful kind.

## Ready-to-execute summary

Use these decisions when Ryan says to execute:

- Start from the top of the curriculum.
- First active area: Prompt Engineering, first/top lab.
- README framing: `Course Progress Log`.
- Create both the README update and the `labs/` + `docs/lab-template.md` scaffold.
- Update `AGENTS.md` so future assistants treat the repo as an AI-led educational exercise using the Socratic method.
- Do not include target roles, contact info, or additional public artifact links.
- Keep claims conservative until lab evidence exists.
