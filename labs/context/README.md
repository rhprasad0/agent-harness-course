# Context Engineering Labs

Status: **Passed — first context-rot slice**

Context Engineering work has started with a local Llama2 context-rot probe. The first slice built a small Ollama harness, varied context length and answer placement, and recorded strict answer-only accuracy plus actual `prompt_eval_count` from Ollama.

When this section begins, document how context is selected, structured, compressed, retrieved, or omitted. The key question is not only "what did the model see?" but "why was that the right window for this step?"

## Evidence log

| Date | Lab | Status | Evidence | Notes |
|---|---|---:|---|---|
| 2026-06-03 | Context Engineering section | Planned | Scaffold only | Not started yet. |
| 2026-06-12 | Llama2 context-rot / lost-in-the-middle probe | Passed — first slice | [`2026-06-12-context-rot-llama2.md`](./2026-06-12-context-rot-llama2.md), [`results/2026-06-12T140407Z-context-rot-llama2-summary.md`](./results/2026-06-12T140407Z-context-rot-llama2-summary.md) | Clean-window run did not support the lost-in-the-middle hypothesis; middle placement scored 3/3 at the long setting, while the original 3072-target run saturated Llama2's 4096-token context boundary. |

## Socratic starter questions

1. What information does the model need that is not in the prompt itself?
2. What context would be harmful, stale, distracting, or too expensive to include?
3. What rule chooses context for the next model call?
4. How will I verify that context selection helped rather than just made the output longer?
