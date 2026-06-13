# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T203503Z`
- Condition: `mission_brief_hand_prompt_v3_train_tuned_heldout_once`
- Model: `llama3:latest`
- Prompt: `labs/context/prompts/mission_brief_router_handwritten_v3_train_tuned.txt`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 9
- Exact route matches: 9 / 9
- Mean required-tool recall: 1.0
- Forbidden tool violations: 0
- Mean unnecessary tools: 0
- Parse errors: 0
- Schema errors: 0
- Wrong clarification flags: 0
- Mean composite score: 1.0
- Mean prompt words: 586.4
- Mean catalog tools: 3
- Mean Ollama prompt eval count: 1238.4
- Failure counts: correct=9

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
