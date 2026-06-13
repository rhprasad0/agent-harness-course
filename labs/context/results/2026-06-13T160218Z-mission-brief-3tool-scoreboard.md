# Mission Brief 3-Tool Routing Smoke Scoreboard

Status: **Smoke-tested scaffold, not final hand-written baseline**

These runs exercise the slim three-tool workflow with a temporary assistant-authored smoke prompt and an uncompiled DSPy signature. Ryan still needs to write the real hand baseline policy.

| Condition | Rows | Exact route | Required recall | Wrong clarification | Overselect avg | Parse errors | Schema errors | Avg prompt words | Avg catalog tools | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `mission_brief_3tool_smoke_prompt` | 6 | 2 / 6 | 0.833 | 3 | 0 | 0 | 0 | 362.7 | 3 | [`summary`](./2026-06-13T160140Z-tool-routing-mission_brief_3tool_smoke_prompt-summary.md) |
| `mission_brief_3tool_dspy_uncompiled_smoke` | 6 | 2 / 6 | 0.417 | 2 | 0.5 | 1 | 0 | 193.7 | 3 | [`summary`](./2026-06-13T160156Z-tool-routing-mission_brief_3tool_dspy_uncompiled_smoke-summary.md) |
| `mission_brief_3tool_dspy_uncompiled_smoke_max1024` | 6 | 3 / 6 | 0.583 | 1 | 0.5 | 0 | 0 | 193.7 | 3 | [`summary`](./2026-06-13T160218Z-tool-routing-mission_brief_3tool_dspy_uncompiled_smoke_max1024-summary.md) |

## Interpretation

- The slim catalog now has exactly three tools: `evidence_reader`, `brief_drafter`, and `human_review_gate`.
- The plain smoke prompt produced valid JSON across 6/6 rows with zero schema failures.
- The first DSPy smoke at `max_tokens=512` had one parse/truncation failure; rerunning at `max_tokens=1024` removed parse failures.
- The remaining failures are routing failures, especially missing required tools and clarification flag errors, which is the intended learning surface.
- This is scaffold evidence, not a final claim about the hand-written prompt or DSPy optimization.
