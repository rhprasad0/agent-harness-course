# Tool Routing Evaluation Summary

- Run ID: `2026-06-13T165137Z`
- Condition: `mission_brief_3tool_dspy_uncompiled_all_max1024`
- Model: `ollama_chat/llama3:latest`
- Prompt: `DSPy Signature: RouteTools`
- Catalog: `labs/context/fixtures/mission_brief_3tool_catalog.json`
- Tasks: `labs/context/fixtures/mission_brief_3tool_tasks.jsonl`
- Preselect: `False`
- Rows: 24
- Exact route matches: 12 / 24
- Mean required-tool recall: 0.625
- Forbidden tool violations: 0
- Mean unnecessary tools: 0.375
- Parse errors: 0
- Schema errors: 0
- Wrong clarification flags: 3
- Mean composite score: 0.556
- Mean prompt words: 193.5
- Mean catalog tools: 3
- Mean Ollama prompt eval count:
- Failure counts: correct=12, missing_required_tool=12, overselected_context=6, wrong_clarification=3

## Notes

This is a synthetic routing evaluation. It does not execute any selected tools and does not use real operational data.
