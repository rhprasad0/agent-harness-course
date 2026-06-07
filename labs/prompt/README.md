# Prompt Engineering Labs

Status: **Passed — two lab slices**

Ryan started from the top of the curriculum here and now has two completed prompt-lab slices with public-safe evidence.

## Current focus

- Keep completed prompt-lab evidence inspectable and conservative.
- Use the AI assistant Socratically: hypothesis first, hints second, direct execution when needed.
- Next: decide whether to deepen prompt experiments or move into Context Engineering.

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | First/top Prompt Engineering module | Starting | Scaffold only | No completed lab evidence yet. |
| 2026-06-04 | Recruiter-facing few-shot order sensitivity | Passed | [`2026-06-04-recruiter-screen-order-sensitivity.md`](./2026-06-04-recruiter-screen-order-sensitivity.md) | Fake candidate fixture + runner implemented; Ollama `gpt-oss:20b` showed borderline-only flips; Codex bridge `gpt-5.5` and Ollama Meta `llama3` showed no flips in first single-run comparisons. |
| 2026-06-06 | GSM8K self-consistency | Passed | [`results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md) | Minimal Ollama/Python harness sampled `mistral:7b-instruct-q4_K_M`; majority voting improved from 36/100 at N=1 to 55/100 at N=10 on the first 100 GSM8K test rows. |

## Next lab note

Create the next detailed note from [`../../docs/lab-template.md`](../../docs/lab-template.md) when the next lab is attempted.

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
