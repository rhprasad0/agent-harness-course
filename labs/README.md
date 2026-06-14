# Lab Index

This directory is Ryan's course-progress ledger for the Agent Engineering Trilogy.

The curriculum itself lives in [`../index.html`](../index.html) and at [`harnesscourse.com`](https://harnesscourse.com). These lab notes are the evidence trail: what Ryan attempted, what the AI assistant helped with, what was verified, what failed, and what comes next.

## Progress ledger

| Area | Status | Notes |
|---|---:|---|
| [Prompt Engineering](./prompt/) | Complete — three lab slices | Completed a recruiter-facing few-shot order-sensitivity lab, a GSM8K self-consistency harness run, and an automatic prompt optimization / GEPA lab with conservative negative held-out evidence. |
| [Context Engineering](./context/) | Complete — LongMemEval/DSPy final-lab slice wrapped | Built a local Ollama/Llama2 context-rot harness; narrowed the Context Module 09 router to three tools; loop-engineered the router prompt to 15/15 on smoke+train and 9/9 heldout once; then wrapped Module 12 with the real LongMemEval cleaned dataset and a simple DSPy reader. The non-official Codex `gpt-5.4` judged rerun confirmed the frozen-reader weakness, and structured context plus evidence-first output improved `answer_sessions` from 0/3 to 1/3 on the first-three dev slice. |
| [Harness Engineering](./harness/) | Not started — planned labs listed | Planned labs are documented, but no Harness Engineering lab evidence has been produced yet. |
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
