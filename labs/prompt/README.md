# Prompt Engineering Labs

Status: **Starting**

Ryan is starting from the top of the curriculum here.

## Current focus

- Begin with the first Prompt Engineering module.
- Use the AI assistant Socratically: hypothesis first, hints second, direct execution when needed.
- Record what changed between expected and observed model behavior.

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | First/top Prompt Engineering module | Starting | Scaffold only | No completed lab evidence yet. |
| 2026-06-04 | Recruiter-facing few-shot order sensitivity | Passed | [`2026-06-04-recruiter-screen-order-sensitivity.md`](./2026-06-04-recruiter-screen-order-sensitivity.md) | Fake candidate fixture + runner implemented; Ollama `gpt-oss:20b` showed borderline-only flips; Codex bridge `gpt-5.5` and Ollama Meta `llama3` showed no flips in first single-run comparisons. |

## Next lab note

Create the first detailed note from [`../../docs/lab-template.md`](../../docs/lab-template.md) once the first prompt lab is attempted.

Suggested filename pattern:

```text
YYYY-MM-DD-<short-lab-name>.md
```

## Socratic starter questions

Before asking the assistant to implement or critique the first prompt lab, Ryan should answer:

1. What is the model supposed to do?
2. What behavior do I expect from the first attempt?
3. What failure mode am I watching for?
4. How will I know whether the prompt improved or merely changed the output?
