# Context Engineering Labs

Status: **In progress — context-rot slice passed; Module 09 loop-engineered routing prompt**

Context Engineering work has started with a local Llama2 context-rot probe and a Context Module 09 tool/context-routing scaffold. The first slice built a small Ollama harness, varied context length and answer placement, and recorded strict answer-only accuracy plus actual `prompt_eval_count` from Ollama. The Module 09 scaffold was narrowed from an overbuilt 26-tool logistics router to a three-tool Mission Brief Intake Router: read evidence, draft a brief, or stop for human review. Ryan's hand-written baseline and an uncompiled DSPy router both ran on the full 24-row slice, then a loop-engineering pass used smoke+train failure analysis to improve the hand prompt before a single heldout check.

When this section begins, document how context is selected, structured, compressed, retrieved, or omitted. The key question is not only "what did the model see?" but "why was that the right window for this step?"

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | Context Engineering section | Planned | Scaffold only | Not started yet. |
| 2026-06-12 | Llama2 context-rot / lost-in-the-middle probe | Passed — first slice | [`2026-06-12-context-rot-llama2.md`](./2026-06-12-context-rot-llama2.md), [`results/2026-06-12T140407Z-context-rot-llama2-summary.md`](./results/2026-06-12T140407Z-context-rot-llama2-summary.md) | Clean-window run did not support the lost-in-the-middle hypothesis; middle placement scored 3/3 at the long setting, while the original 3072-target run saturated Llama2's 4096-token context boundary. |
| 2026-06-13 | Context Module 09 three-tool routing | Attempted — full baseline/DSPy comparison run | [`2026-06-13-tool-skill-routing-context-construction.md`](./2026-06-13-tool-skill-routing-context-construction.md), [`results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md`](./results/2026-06-13T165137Z-mission-brief-3tool-baseline-vs-dspy.md) | Over-scoped logistics router was narrowed to a Mission Brief Intake Router with three tools: `evidence_reader`, `brief_drafter`, and `human_review_gate`. Ryan's hand-written baseline beat uncompiled DSPy on required-tool recall/composite; DSPy had more exact-route matches, fewer clarification mistakes, and shorter context. |
| 2026-06-13 | Context Module 09 loop engineering | Passed target — train-tuned prompt plus one heldout check | [`results/2026-06-13T203503Z-mission-brief-router-train-tuned-scoreboard.md`](./results/2026-06-13T203503Z-mission-brief-router-train-tuned-scoreboard.md), [`prompts/mission_brief_router_handwritten_v3_train_tuned.txt`](./prompts/mission_brief_router_handwritten_v3_train_tuned.txt) | Loop engineering made the process explicit: inspect wrong rows, revise the routing policy, rerun the same harness, and stop on a predefined target. The v3 prompt reached 15/15 on smoke+train and 9/9 on one heldout run; caveat: tiny synthetic fixture, train-tuned result. |

## Socratic starter questions

1. What information does the model need that is not in the prompt itself?
2. What context would be harmful, stale, distracting, or too expensive to include?
3. What rule chooses context for the next model call?
4. How will I verify that context selection helped rather than just made the output longer?
