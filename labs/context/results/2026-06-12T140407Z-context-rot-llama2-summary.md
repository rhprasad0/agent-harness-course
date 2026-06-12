# Context Rot Llama2 Summary — 2026-06-12T140407Z

## Run configuration

- Model: `llama2:7b-chat-q4_0`
- `num_ctx`: `4096`
- `num_predict`: `64`
- Temperature: `0.0`
- Target context tokens: `512,1536,2300`
- Positions: `beginning,middle,end`
- Repeats per cell: `3`
- Expected answer: `mango-orbit-92`

## Overall result

- Correct: 24/27
- Failure counts: correct=24, extra_text=3

## Accuracy by target length and position

| Target context tokens | Observed avg prompt eval tokens | Position | Correct / Trials | Accuracy | Avg seconds | Failure counts |
|---:|---:|---|---:|---:|---:|---|
| 512 | 792.7 | beginning | 3/3 | 1.000 | 0.631 | correct=3 |
| 512 | 773.7 | end | 3/3 | 1.000 | 0.502 | correct=3 |
| 512 | 797.3 | middle | 3/3 | 1.000 | 0.526 | correct=3 |
| 1536 | 2192.7 | beginning | 3/3 | 1.000 | 1.076 | correct=3 |
| 1536 | 2205.3 | end | 3/3 | 1.000 | 1.226 | correct=3 |
| 1536 | 2184 | middle | 3/3 | 1.000 | 1.227 | correct=3 |
| 2300 | 3267.3 | beginning | 1/3 | 0.333 | 1.719 | correct=1; extra_text=2 |
| 2300 | 3225.7 | end | 2/3 | 0.667 | 1.76 | correct=2; extra_text=1 |
| 2300 | 3273 | middle | 3/3 | 1.000 | 1.811 | correct=3 |

## First failure examples

- `long-beginning-001` (extra_text): `The answer to the question is: mango-orbit-92`
- `long-beginning-002` (extra_text): `The answer is: mango-orbit-92`
- `long-end-001` (extra_text): `The Project Lantern access code is mango-orbit-92.`
