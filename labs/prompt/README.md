# Prompt Engineering Labs

Status: **Complete — three lab slices**

Ryan started from the top of the curriculum here and now has three completed prompt-lab slices with public-safe evidence.

## Current focus

- Keep completed prompt-lab evidence inspectable and conservative.
- Use the AI assistant Socratically: hypothesis first, hints second, direct execution when needed.
- Next: use the prompt-lab evidence as a baseline while moving into Harness Engineering.

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | First/top Prompt Engineering module | Starting | Scaffold only | No completed lab evidence yet. |
| 2026-06-04 | Recruiter-facing few-shot order sensitivity | Passed | [`2026-06-04-recruiter-screen-order-sensitivity.md`](./2026-06-04-recruiter-screen-order-sensitivity.md) | Fake candidate fixture + runner implemented; Ollama `gpt-oss:20b` showed borderline-only flips; Codex bridge `gpt-5.5` and Ollama Meta `llama3` showed no flips in first single-run comparisons. |
| 2026-06-06 | GSM8K self-consistency | Passed | [`results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md`](./results/2026-06-06T175239Z-gsm8k-test-first100-ollama-mistral-7b-instruct-q4_K_M-self-consistency-summary.md) | Minimal Ollama/Python harness sampled `mistral:7b-instruct-q4_K_M`; majority voting improved from 36/100 at N=1 to 55/100 at N=10 on the first 100 GSM8K test rows. |
| 2026-06-07 | Automatic prompt optimization / GEPA | Attempted | [`2026-06-07-automatic-prompt-optimization.md`](./2026-06-07-automatic-prompt-optimization.md), [`results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md`](./results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304-summary.md) | Built a fixed GSM8K prompt evaluator plus APE and DSPy/GEPA comparison artifacts. The largest Llama3 split tied baseline at 138/200, so the result is useful negative evidence rather than a claimed prompt-optimization win. |

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
