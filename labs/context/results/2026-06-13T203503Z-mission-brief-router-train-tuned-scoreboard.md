# Mission Brief Router Train-Tuned Iteration Scoreboard

Status: **success target met**

This artifact records a non-overfit-ish lab loop: variants were developed against smoke+train rows only, then the selected v3 hand prompt was evaluated on heldout once. Fixtures, gold labels, schema, and catalog were not edited.

## Scoreboard

| Candidate | Split | Role | Exact route | Required recall | Wrong clarification | Overselect avg | Parse errors | Schema errors | Composite | Evidence |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Original hand prompt | smoke+train | baseline | 4 / 15 | 0.833 | 8 | 0.533 | 0 | 0 | 0.647 | [`jsonl`](./2026-06-13T165105Z-tool-routing-mission_brief_3tool_hand_prompt_all.jsonl) |
| Original DSPy typed router | smoke+train | baseline | 8 / 15 | 0.633 | 2 | 0.4 | 0 | 0 | 0.56 | [`jsonl`](./2026-06-13T165137Z-tool-routing-mission_brief_3tool_dspy_uncompiled_all_max1024.jsonl) |
| Hand prompt v2 train-tuned | smoke+train | iteration 1 | 7 / 15 | 0.7 | 1 | 0.067 | 0 | 0 | 0.677 | [`jsonl`](./2026-06-13T203346Z-tool-routing-mission_brief_hand_prompt_v2_train_tuned_smoke_train.jsonl) |
| Hand prompt v3 train-tuned | smoke+train | iteration 2 / selected | 15 / 15 | 1.0 | 0 | 0.0 | 0 | 0 | 1.0 | [`jsonl`](./2026-06-13T203439Z-tool-routing-mission_brief_hand_prompt_v3_train_tuned_smoke_train.jsonl) |
| Hand prompt v3 train-tuned | heldout once | final holdout | 9 / 9 | 1.0 | 0 | 0.0 | 0 | 0 | 1.0 | [`jsonl`](./2026-06-13T203503Z-tool-routing-mission_brief_hand_prompt_v3_train_tuned_heldout_once.jsonl) |

## Result

- Iteration stopped after v3 because it exceeded the iteration target: `15/15` on smoke+train with zero parse/schema errors.
- The single heldout run also met the target: `9/9` with zero parse/schema errors.
- Report this as train-tuned/in-sample prompt improvement plus a one-shot heldout check on a tiny synthetic fixture, not as broad model generalization.

## Prompt change summary

The successful v3 prompt made `evidence_state` authoritative, added an ordered decision table, and explicitly called out the prior failure classes: provided+draft requires both read and draft; inline-only rewrite requires draft only; conflicting/sensitive requires read plus human review; authority actions require human review only.
