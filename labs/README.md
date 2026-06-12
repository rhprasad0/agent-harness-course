# Lab Index

This directory is Ryan's course-progress ledger for the Agent Engineering Trilogy.

The curriculum itself lives in [`../index.html`](../index.html) and at [`harnesscourse.com`](https://harnesscourse.com). These lab notes are the evidence trail: what Ryan attempted, what the AI assistant helped with, what was verified, what failed, and what comes next.

## Progress ledger

| Area | Status | Notes |
|---|---:|---|
| [Prompt Engineering](./prompt/) | Passed — three lab slices | Completed a recruiter-facing few-shot order-sensitivity lab, a GSM8K self-consistency harness run, and an automatic prompt optimization / GEPA lab with conservative negative held-out evidence. |
| [Context Engineering](./context/) | Passed — first lab slice | Built a local Ollama/Llama2 context-rot harness. Clean-window run did not support lost-in-the-middle on the fixed synthetic fact; boundary run showed why recording actual `prompt_eval_count` matters. |
| [Harness Engineering](./harness/) | Planned | Not started yet. |
| [Capstone](./capstone/) | Planned | Not started yet. |

## Lab note standard

Use [`../docs/lab-template.md`](../docs/lab-template.md) for new lab notes.

Every substantive lab entry should capture:

- objective,
- hypothesis or expected failure mode,
- Socratic prompts or hints used,
- implementation attempt,
- verification command/output,
- result,
- surprise or failure,
- next step,
- recruiter-agent inspection notes.

Do not invent progress. Early scaffolding is useful, but it is not the same thing as completed lab evidence.
