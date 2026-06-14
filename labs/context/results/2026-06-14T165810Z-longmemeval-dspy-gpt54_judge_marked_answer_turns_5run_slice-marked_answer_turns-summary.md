# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T165810Z`
Condition: `gpt54_judge_marked_answer_turns_5run_slice`
Dataset: `labs/context/data/longmemeval/longmemeval_oracle.json`
Model: `ollama_chat/llama3:latest`
Context policy: `marked_answer_turns`
Judge provider/model: `codex-bridge` / `gpt-5.4`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| marked_answer_turns | 15 | 3 | 5 | 0.333 | 0 | 0.333 | 0.222 | 1.000 | 0.667 | 0.922 | 1.000 | n/a | 0 | 142.7 | 0.43 |

## Notes

- Headline QA accuracy is GPT-4o judge accuracy when `--judge-provider codex-bridge --judge-model gpt-4o` succeeds.
- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.
- Embedding semantic grounding is diagnostic and not an official LongMemEval score.
- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.

## Row sample

### gpt4_2655b836 repeat 1

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_2487a7cb repeat 1

- Type: `temporal-reasoning`
- Question: Which event did I attend first, the 'Effective Time Management' workshop or the 'Data Analysis using Python' webinar?
- Gold: 'Data Analysis using Python' webinar
- Pred: The 'Effective Time Management' workshop.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_76048e76 repeat 1

- Type: `temporal-reasoning`
- Question: Which vehicle did I take care of first in February, the bike or the car?
- Gold: bike
- Pred: The bike.
- GPT-4o judge correct: `True`; judge error: ``
- Heuristic correct: `True`; F1: `0.667`; evidence hit: `True`

### gpt4_2655b836 repeat 2

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_2487a7cb repeat 2

- Type: `temporal-reasoning`
- Question: Which event did I attend first, the 'Effective Time Management' workshop or the 'Data Analysis using Python' webinar?
- Gold: 'Data Analysis using Python' webinar
- Pred: I attended the 'Effective Time Management' workshop first.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`
