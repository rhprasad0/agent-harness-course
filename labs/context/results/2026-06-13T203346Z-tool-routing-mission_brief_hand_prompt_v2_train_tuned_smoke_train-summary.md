# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T203346Z`
- Condition: `mission_brief_hand_prompt_v2_train_tuned_smoke_train`
- Model: `llama3:latest`
- Prompt: `labs/context/prompts/mission_brief_router_handwritten_v2_train_tuned.txt`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 15
- Exact route matches: 7 / 15
- Mean required-tool recall: 0.7
- Forbidden tool violations: 0
- Mean unnecessary tools: 0.067
- Parse errors: 0
- Schema errors: 0
- Wrong clarification flags: 1
- Mean composite score: 0.677
- Mean prompt words: 709.5
- Mean catalog tools: 3
- Mean Ollama prompt eval count: 1347.5
- Failure counts: correct=7, missing_required_tool=8, overselected_context=1, wrong_clarification=1

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
