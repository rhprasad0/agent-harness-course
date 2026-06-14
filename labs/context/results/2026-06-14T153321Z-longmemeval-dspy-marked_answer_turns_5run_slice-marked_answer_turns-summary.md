# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T153321Z`
Condition: `marked_answer_turns_5run_slice`
Dataset: `labs/context/data/longmemeval/longmemeval_oracle.json`
Model: `ollama_chat/llama3:latest`
Context policy: `marked_answer_turns`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | Accuracy | Accuracy stdev | Mean F1 | Evidence hit | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| marked_answer_turns | 15 | 3 | 5 | 0.333 | 0.471 | 0.222 | 1.000 | 0 | 142.7 | 0.42 |

## Notes

- Scoring is a lightweight local heuristic: normalized substring match or token F1 >= 0.80.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.
- Treat this as a harness smoke / small-slice lab artifact, not a LongMemEval leaderboard result.

## Row sample

### gpt4_2655b836 repeat 1

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_2487a7cb repeat 1

- Type: `temporal-reasoning`
- Question: Which event did I attend first, the 'Effective Time Management' workshop or the 'Data Analysis using Python' webinar?
- Gold: 'Data Analysis using Python' webinar
- Pred: I attended the 'Effective Time Management' workshop first.
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_76048e76 repeat 1

- Type: `temporal-reasoning`
- Question: Which vehicle did I take care of first in February, the bike or the car?
- Gold: bike
- Pred: The bike.
- Correct: `True`; F1: `0.667`; evidence hit: `True`

### gpt4_2655b836 repeat 2

- Type: `temporal-reasoning`
- Question: What was the first issue I had with my new car after its first service?
- Gold: GPS system not functioning correctly
- Pred: I don't know.
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### gpt4_2487a7cb repeat 2

- Type: `temporal-reasoning`
- Question: Which event did I attend first, the 'Effective Time Management' workshop or the 'Data Analysis using Python' webinar?
- Gold: 'Data Analysis using Python' webinar
- Pred: I attended the 'Effective Time Management' workshop first.
- Correct: `False`; F1: `0.000`; evidence hit: `True`
