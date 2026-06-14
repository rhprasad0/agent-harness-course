# Harness Engineering Labs

Status: **Not started — planned labs listed**

Harness Engineering work has not started yet. The planned lab sequence below mirrors the curriculum labs in `index.html`; these rows are placeholders, not evidence.

This is the portion where Ryan will build the control program around model calls: state, tools, loops, retries, verifiers, and termination conditions. A coding agent may help, but the design should remain explainable by Ryan.

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | Harness Engineering section | Planned | Scaffold only | Not started yet. |
| 2026-06-14 | Module 02 — minimal ReAct loop | Not started | Planned | Implement a minimal ReAct loop in about 100 lines, no framework. |
| 2026-06-14 | Module 03 — tool registry failure modes | Not started | Planned | Build a tool registry with bad arguments, missing resource, and timeout cases; observe recovery behavior. |
| 2026-06-14 | Module 06 — progressive tool disclosure | Not started | Planned | Route among tool clusters before exposing selected tool descriptions to the main agent. |
| 2026-06-14 | Module 10 — OpenInference tracing | Not started | Planned | Instrument the ReAct agent end-to-end, introduce a bug, and find it in the trace. |
| 2026-06-14 | Module 12 — Meta-Harness-style final lab | Not started | Planned | Run a small outer loop over the semester harness and compare automated edits with the hand-tuned version. |
| 2026-06-14 | Addendum — specialized harness | Not started | Planned | Specialize the ReAct loop for a bounded SOP-like task family with typed state, scoped tools, validation checks, and a task metric. |

## Socratic starter questions

1. What is the smallest useful harness loop?
2. What state must persist between model calls?
3. What tools are exposed, and what side effects can they have?
4. What stops the loop?
5. What verifies that the model did the right thing?
6. What failure mode should the first harness intentionally handle?
