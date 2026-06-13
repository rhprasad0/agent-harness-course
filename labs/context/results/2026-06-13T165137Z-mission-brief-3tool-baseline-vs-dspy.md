# Mission Brief 3-Tool Routing Baseline vs DSPy

Status: **Full 24-row comparison complete**

This compares Ryan's hand-written baseline prompt against an uncompiled DSPy typed router on the same 24 synthetic Mission Brief Intake Router rows. Neither condition executes tools; both only select tools and are scored against assistant-drafted gold labels for Ryan review.

## Overall results

| Condition | Rows | Exact route | Required recall | Wrong clarification | Overselect avg | Parse errors | Schema errors | Composite | Avg prompt words | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `hand_prompt_baseline` | 24 | 8 / 24 | 0.854 | 12 | 0.458 | 0 | 0 | 0.683 | 579.5 | [`summary`](./2026-06-13T165105Z-tool-routing-mission_brief_3tool_hand_prompt_all-summary.md) |
| `dspy_uncompiled` | 24 | 12 / 24 | 0.625 | 3 | 0.375 | 0 | 0 | 0.556 | 193.5 | [`summary`](./2026-06-13T165137Z-tool-routing-mission_brief_3tool_dspy_uncompiled_all_max1024-summary.md) |

## By split

| Condition | Split | Rows | Exact route | Required recall | Wrong clarification | Overselect avg | Composite |
|---|---|---:|---:|---:|---:|---:|---:|
| `hand_prompt_baseline` | `smoke` | 6 | 1 / 6 | 0.833 | 3 | 0.5 | 0.658 |
| `hand_prompt_baseline` | `train` | 9 | 3 / 9 | 0.833 | 5 | 0.556 | 0.639 |
| `hand_prompt_baseline` | `heldout` | 9 | 4 / 9 | 0.889 | 4 | 0.333 | 0.744 |
| `dspy_uncompiled` | `smoke` | 6 | 3 / 6 | 0.583 | 1 | 0.5 | 0.492 |
| `dspy_uncompiled` | `train` | 9 | 5 / 9 | 0.667 | 1 | 0.333 | 0.606 |
| `dspy_uncompiled` | `heldout` | 9 | 4 / 9 | 0.611 | 1 | 0.333 | 0.55 |

## Interpretation

- The hand-written baseline had higher required-tool recall (`0.854` vs `0.625`) and higher composite score (`0.683` vs `0.556`).
- The DSPy typed router had more exact route matches (`12/24` vs `8/24`) and far fewer clarification mistakes (`3` vs `12`).
- DSPy used a much shorter prompt/context shape (`~193` words vs `~580` words), which is useful context-engineering evidence even though recall fell.
- Both conditions had zero parse errors and zero schema errors on the full run.
- Provisional takeaway: DSPy made the boundary more structured and concise, but it under-selected required tools. The hand prompt remembers to read/draft more often but is shakier on when to stop.
