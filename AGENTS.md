# Agent Instructions

## Repository Purpose

This repo is both:

1. A static curriculum artifact for the Agent Engineering Trilogy.
2. Ryan's AI-led course-progress workspace for working through the labs with an assistant.

The production page is `index.html`; `harness-engineering-curriculum.html` is only a small compatibility redirect for older links. The lab documentation in `labs/` is Ryan's progress trail, not a replacement for the curriculum page.

## AI-led lab workflow

Future agents should act like Socratic lab coaches, not answer vending machines.

Default loop:

1. Ask Ryan to state the goal, hypothesis, design choice, or expected failure mode.
2. Offer one or two hints before giving a full solution.
3. When Ryan asks to execute, is blocked, or correctness/safety requires it, implement directly and verify with real outputs.
4. Record useful lab results in `labs/` using `docs/lab-template.md`.
5. Keep claims conservative: mark work as planned, starting, attempted, passed, failed, or inconclusive.

The point is to build learning reps and public evidence. Let Ryan do as much reasoning as practical; the AI can scaffold, inspect, verify, debug, and document. Tiny gym whistle optional.

## Lab documentation rules

- Use `labs/README.md` as the lab index.
- Keep Prompt, Context, Harness, and Capstone notes under their matching `labs/` subdirectories.
- Lab notes should capture objective, hypothesis, attempt, verification, result, failure/surprise, and next step.
- Do not invent progress. Placeholders stay clearly labeled as planned or starting.
- Course labs are learning artifacts, not customer production deployments.

## Production Site

- Intended production domain: `harnesscourse.com`
- Repository visibility: public
- Hosting target: GitHub Pages, deployed from the root of `main`
- Root entrypoint: `index.html`, which serves the curriculum directly
- Legacy direct-file path: `harness-engineering-curriculum.html`, which redirects to `index.html`
- GitHub Pages custom-domain file: `CNAME`

Porkbun DNS records: apex `ALIAS` to `vivekhaldar.github.io`; `www` `CNAME` to `vivekhaldar.github.io`. Do not put registrar order IDs, billing details, renewal dates, account settings, secrets, tokens, credentials, private IPs, or PII in this public repository.

GitHub Pages status as of 2026-05-27: Pages is enabled for `main` `/` with `harnesscourse.com` as the custom domain. HTTPS enforcement may remain unavailable immediately after DNS setup until GitHub issues the custom-domain certificate. If `https_enforced` is still false later, retry the Pages update after the certificate exists.

Expected Porkbun DNS records:

```text
ALIAS  @    vivekhaldar.github.io
CNAME  www  vivekhaldar.github.io
```

If ALIAS flattening cannot be used, configure the GitHub Pages apex A records:

```text
A  @  185.199.108.153
A  @  185.199.109.153
A  @  185.199.110.153
A  @  185.199.111.153
```

To enable HTTPS once the GitHub Pages certificate exists:

```sh
gh api --method PUT repos/vivekhaldar/agent-engineering-trilogy/pages \
  -F cname=harnesscourse.com \
  -F https_enforced=true \
  -F 'source[branch]=main' \
  -F 'source[path]=/'
```

## Working Rules

- Treat `index.html` as the product. Keep it directly openable in a browser.
- Keep curriculum content in `index.html` only; do not duplicate it into `harness-engineering-curriculum.html` or lab notes.
- Do not use symlinks for published Pages files; GitHub Pages artifacts must not contain symbolic or hard links.
- Do not add a framework, package manager, bundler, or generated asset pipeline unless explicitly asked.
- Keep the curriculum structure in this order: Prompt Engineering, Context Engineering, Harness Engineering, Capstone.
- Prefer inline links to stable primary sources. Bibliography-only links are not enough when the prose names a specific paper, article, or project.
- Preserve the existing visual language and typography unless the task is explicitly a redesign.
- Make edits in small, logical commits and stage files by name.
- After deployment-related edits, verify that `CNAME` still contains exactly `harnesscourse.com`.

## Verification

For content-only edits:

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

For lab-documentation updates, also check the expected public-facing markers:

```sh
rg -n "Course Progress Log|Lab evidence log|Recruiter-agent|AI-led lab workflow|Socratic" README.md AGENTS.md labs docs
```

For JavaScript or table-of-contents behavior edits, also validate the inline script syntax:

```sh
node - <<'NODE'
const fs = require('fs');
for (const path of ['index.html', 'harness-engineering-curriculum.html']) {
  const html = fs.readFileSync(path, 'utf8');
  const scripts = Array.from(html.matchAll(/<script>([\s\S]*?)<\/script>/g));
  if (scripts.length === 0) throw new Error(`No inline script found in ${path}`);
  for (const [, script] of scripts) new Function(script);
  console.log(`${path}: inline script syntax ok`);
}
NODE
```

When possible, open the page locally after edits and skim the affected section in the browser.
