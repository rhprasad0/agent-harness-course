# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T160156Z`
- Condition: `mission_brief_3tool_dspy_uncompiled_smoke`
- Model: `ollama_chat/llama3:latest`
- Prompt: `DSPy Signature: RouteTools`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 6
- Exact route matches: 2 / 6
- Mean required-tool recall: 0.417
- Forbidden tool violations: 0
- Mean unnecessary tools: 0.5
- Parse errors: 1
- Schema errors: 0
- Wrong clarification flags: 2
- Mean composite score: 0.158
- Mean prompt words: 193.7
- Mean catalog tools: 3
- Mean Ollama prompt eval count:
- Failure counts: correct=2, missing_required_tool=3, overselected_context=2, parse_error=1, wrong_clarification=1

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
