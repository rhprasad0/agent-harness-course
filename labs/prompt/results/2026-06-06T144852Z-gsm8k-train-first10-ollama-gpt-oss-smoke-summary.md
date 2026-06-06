# GSM8K Ollama GPT-OSS Smoke Test

- Date: 2026-06-06T144852Z
- Model: `gpt-oss:20b` via Ollama `http://127.0.0.1:11434`
- Dataset: `labs/prompt/data/gsm8k/train.jsonl`
- Slice: first 10 training questions
- Temperature: 0.0
- Result: 10/10 correct (100.0%)
- Average elapsed: 3.75s/question
- Average completion tokens reported by Ollama: 257.0

| # | Correct | Pred | Gold | Question |
|---:|:---:|---:|---:|---|
| 1 | ✅ | 72 | 72 | Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Nat... |
| 2 | ✅ | 10 | 10 | Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn? |
| 3 | ✅ | 5 | 5 | Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents deci... |
| 4 | ✅ | 42 | 42 | Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as... |
| 5 | ✅ | 624 | 624 | James writes a 3-page letter to 2 different friends twice a week.  How many pages does he write a year? |
| 6 | ✅ | 35 | 35 | Mark has a garden with flowers. He planted plants of three different colors in it. Ten of them are yellow, and there ... |
| 7 | ✅ | 48 | 48 | Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza ha... |
| 8 | ✅ | 16 | 16 | Ken created a care package to send to his brother, who was away at boarding school.  Ken placed a box on a scale, and... |
| 9 | ✅ | 41 | 41 | Alexis is applying for a new job and bought a new set of business clothes to wear to the interview. She went to a dep... |
| 10 | ✅ | 990 | 990 | Tina makes $18.00 an hour.  If she works more than 8 hours per shift, she is eligible for overtime, which is paid by ... |

## Notes

This is a smoke test only: no self-consistency yet, no few-shot exemplars, and no full-dataset claim. Tiny sample, tiny trumpet.
Raw JSONL: `labs/prompt/results/2026-06-06T144852Z-gsm8k-train-first10-ollama-gpt-oss-smoke.jsonl`
