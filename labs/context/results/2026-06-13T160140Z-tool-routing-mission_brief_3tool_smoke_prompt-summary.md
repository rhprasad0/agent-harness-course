# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T160140Z`
- Condition: `mission_brief_3tool_smoke_prompt`
- Model: `llama3:latest`
- Prompt: `labs/context/prompts/mission_brief_router_smoke_prompt.txt`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 6
- Exact route matches: 2 / 6
- Mean required-tool recall: 0.833
- Forbidden tool violations: 0
- Mean unnecessary tools: 0
- Parse errors: 0
- Schema errors: 0
- Wrong clarification flags: 3
- Mean composite score: 0.708
- Mean prompt words: 362.7
- Mean catalog tools: 3
- Mean Ollama prompt eval count: 669.2
- Failure counts: correct=2, missing_required_tool=2, wrong_clarification=3

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
