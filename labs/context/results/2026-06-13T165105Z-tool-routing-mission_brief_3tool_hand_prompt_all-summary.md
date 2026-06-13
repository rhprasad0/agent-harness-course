# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T165105Z`
- Condition: `mission_brief_3tool_hand_prompt_all`
- Model: `llama3:latest`
- Prompt: `labs/context/prompts/mission_brief_router_handwritten_v1.txt`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 24
- Exact route matches: 8 / 24
- Mean required-tool recall: 0.854
- Forbidden tool violations: 0
- Mean unnecessary tools: 0.458
- Parse errors: 0
- Schema errors: 0
- Wrong clarification flags: 12
- Mean composite score: 0.683
- Mean prompt words: 579.5
- Mean catalog tools: 3
- Mean Ollama prompt eval count: 1065.5
- Failure counts: correct=8, missing_required_tool=7, overselected_context=11, wrong_clarification=12

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
