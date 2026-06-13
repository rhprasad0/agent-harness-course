# Context Module 09 — Three-Tool Mission Brief Router

Date: 2026-06-13
Status: **Passed target — slim three-tool baseline/DSPy comparison plus loop-engineered prompt**

## Objective

Build a smaller Context Engineering Module 09 experiment that Ryan can reason about directly: a **Mission Brief Intake Router** with exactly three possible tools.

The router chooses whether the agent should:

1. read evidence,
2. draft a brief,
3. stop for human review.

This replaces the earlier 26-tool Joint Logistics Decision Assistant scaffold, which worked mechanically but was too workflow-heavy for the learning objective.

## Hypothesis / expected failure mode

The hard part is not logistics knowledge. The hard part is deciding what the model should be allowed to do next.

Expected failure modes:

- The model drafts when it should stop for human review.
- The model skips evidence reading when the request depends on packet material.
- The model reads evidence unnecessarily when all facts are already inline.
- The model emits valid JSON but routes to the wrong tool set.

## Socratic prompts / hints used

- What workflow are we actually trying to capture?
- Can Ryan explain the workflow without pretending to be a logistics expert?
- What is the smallest tool set that still tests context construction?
- When should the agent read, draft, or stop?
- Is schema success the same as routing success?

## Implementation attempt

Created a slim three-tool fixture set:

- `fixtures/mission_brief_3tool_catalog.json` — exactly three tools: `evidence_reader`, `brief_drafter`, `human_review_gate`.
- `fixtures/mission_brief_3tool_output_schema.json` — strict JSON schema without `selected_skills`.
- `fixtures/mission_brief_3tool_tasks.jsonl` — 24 assistant-drafted rows split into 6 smoke, 9 train, and 9 held-out rows.
- `prompts/mission_brief_router_handwritten_v1.txt` — hand-written prompt scaffold for Ryan.
- `prompts/mission_brief_router_smoke_prompt.txt` — temporary assistant-authored prompt for harness smoke only.

Adapted the evaluators so the slim schema can omit `selected_skills`:

- `scripts/evaluate_tool_routing_prompt.py`
- `scripts/run_tool_routing_dspy.py`

The evaluator still never executes routed tools. It only asks the model to pick tools, parses JSON, and scores the route.

## Verification command/output

Full 24-row baseline vs DSPy comparison:

```text
Hand-written baseline prompt:
Rows: 24
Exact route matches: 8 / 24
Mean required-tool recall: 0.854
Wrong clarification flags: 12
Parse errors: 0
Schema errors: 0
Mean composite score: 0.683

DSPy uncompiled typed router, max_tokens=1024:
Rows: 24
Exact route matches: 12 / 24
Mean required-tool recall: 0.625
Wrong clarification flags: 3
Parse errors: 0
Schema errors: 0
Mean composite score: 0.556
```

Comparison artifact:

- `results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md`

Interpretation: the hand-written baseline had better required-tool recall and composite score, while the uncompiled DSPy router had more exact-route matches, far fewer clarification mistakes, and a much shorter prompt/context shape. This is a useful context-engineering tradeoff: typed routing made the boundary crisper, but it under-selected required tools.

Earlier scaffold smoke:

Fixture validation:

```text
3-tool fixture validation ok
{'smoke': 6, 'train': 9, 'heldout': 9}
```

Plain evaluator dry run:

```text
Rows: 2
Parse errors: 0
Schema errors: 0
Mean catalog tools: 3
```

Plain evaluator smoke with temporary prompt and `llama3:latest`:

```text
Rows: 6
Exact route matches: 2 / 6
Mean required-tool recall: 0.833
Forbidden tool violations: 0
Mean unnecessary tools: 0
Parse errors: 0
Schema errors: 0
Wrong clarification flags: 3
Mean prompt words: 362.7
Mean catalog tools: 3
Mean Ollama prompt eval count: 669.2
```

DSPy uncompiled smoke, first pass at `max_tokens=512`:

```text
Rows: 6
Exact route matches: 2 / 6
Mean required-tool recall: 0.417
Parse errors: 1
Schema errors: 0
```

DSPy uncompiled smoke, rerun at `max_tokens=1024`:

```text
Rows: 6
Exact route matches: 3 / 6
Mean required-tool recall: 0.583
Parse errors: 0
Schema errors: 0
Wrong clarification flags: 1
Mean catalog tools: 3
```

Scoreboard:

- `results/2026-06-13T160218Z-mission-brief-3tool-scoreboard.md`

## Result

The slim workflow scaffold is working.

The important result is not the smoke score. The important result is that the new workflow is explainable:

> A mission staffer asks for help; the router decides whether to read evidence, draft a brief, or stop for human review.

The smoke runs also show that the harness can now test the right failure classes:

- valid JSON but wrong route,
- evidence-read omissions,
- draft-vs-review boundary mistakes,
- DSPy truncation/parse budget issues.

## Failure / surprise

The first DSPy smoke had one parse failure because the response was truncated at `max_tokens=512`. Increasing to `max_tokens=1024` removed the parse failure. This is an environment/harness finding, not a routing-quality result.

The plain smoke prompt still missed clarification behavior on half the smoke rows. That is useful: the final hand-written prompt should probably focus on the **stop/don't draft** boundary.

## Next step

Ryan ran a stricter loop-engineering follow-up: inspect the wrong rows, revise the routing policy, rerun the same fixed harness, stop when a predefined target is met, and only then run heldout once. The loop tuned only against smoke+train rows, then evaluated heldout once:

```text
Original hand prompt on smoke+train: 4 / 15 exact routes
Original DSPy typed router on smoke+train: 8 / 15 exact routes
Hand prompt v2 on smoke+train: 7 / 15 exact routes
Hand prompt v3 on smoke+train: 15 / 15 exact routes
Hand prompt v3 heldout once: 9 / 9 exact routes
```

Scoreboard:

- `results/2026-06-13T203503Z-mission-brief-router-train-tuned-scoreboard.md`

The v3 result should be described conservatively: train-tuned prompt improvement plus a one-shot heldout check on a tiny synthetic fixture, not broad proof that the policy generalizes.

## Recruiter-agent inspection notes

- Claim supported: Ryan narrowed an overbuilt agent-routing lab into a crisp context-construction experiment with a three-tool workflow, strict JSON outputs, smoke-tested evaluators, a 24-row hand-prompt vs DSPy comparison, and a documented loop-engineering pass.
- Evidence path: this note, `fixtures/mission_brief_3tool_*`, `prompts/mission_brief_router_*`, both evaluator scripts, `results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md`, and `results/2026-06-13T203503Z-mission-brief-router-train-tuned-scoreboard.md`.
- Confidence: High that the scaffold runs and captures meaningful routing failures; medium that the loop-engineered v3 result fairly describes this tiny synthetic slice. Gold labels are still assistant-drafted and should be treated as reviewable lab labels, not ground truth about real mission workflows.
- Caveat: All data is synthetic and public-safe; this is a lab harness, not a deployed mission system.
