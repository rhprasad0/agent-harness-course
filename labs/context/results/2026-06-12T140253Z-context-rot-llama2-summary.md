# Context Rot Llama2 Summary — 2026-06-12T140253Z

## Run configuration

- Model: `llama2:7b-chat-q4_0`
- `num_ctx`: `4096`
- `num_predict`: `64`
- Temperature: `0.0`
- Target context tokens: `512`
- Positions: `beginning,middle,end`
- Repeats per cell: `1`
- Expected answer: `mango-orbit-92`

## Overall result

- Correct: 3/3
- Failure counts: correct=3

## Accuracy by target length and position

| Target context tokens | Observed avg prompt eval tokens | Position | Correct / Trials | Accuracy | Avg seconds | Failure counts |
|---:|---:|---|---:|---:|---:|---|
| 512 | 796 | beginning | 1/1 | 1.000 | 2.322 | correct=1 |
| 512 | 774 | end | 1/1 | 1.000 | 0.491 | correct=1 |
| 512 | 804 | middle | 1/1 | 1.000 | 0.509 | correct=1 |

## Failure examples

No failures in this run.
