# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T155035Z`
Condition: `frozen_reader_s_first3_lexical_retrieval`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Context policy: `lexical_retrieval`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | Accuracy | Accuracy stdev | Mean F1 | Evidence hit | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical_retrieval | 15 | 3 | 5 | 0.000 | 0.000 | 0.000 | 0.333 | 0 | 1965.3 | 3.02 |

## Notes

- Scoring is a lightweight local heuristic: normalized substring match or token F1 >= 0.80.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.
- Treat this as a harness smoke / small-slice lab artifact, not a LongMemEval leaderboard result.

## Row sample

### e47becba repeat 1

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `False`

### 118b2229 repeat 1

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I think I can help you with that! Since you're interested in exploring more of the singer-songwriter and Americana genres, I'd recommend checking out local music venues that feature these types of acts. You could also look into local music festivals or events that showcase emerging artists.

Additionally, consider attending open mic nights or songwriting workshops where you can meet other musicians and learn about upcoming shows in your area. You might even discover some hidden gems or new favorite artists!
- Correct: `False`; F1: `0.000`; evidence hit: `False`

### 51a45a95 repeat 1

- Type: `single-session-user`
- Question: Where did I redeem a $5 coupon on coffee creamer?
- Gold: Target
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `True`

### e47becba repeat 2

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- Correct: `False`; F1: `0.000`; evidence hit: `False`

### 118b2229 repeat 2

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I think I can help you with that! Since you're interested in exploring more of the singer-songwriter and Americana genres, I'd recommend checking out some local music venues that host live performances. You could also look into attending local music festivals or events that feature emerging artists.

Additionally, you might want to consider reaching out to local music organizations or community centers that support music education and performance. They often have resources and opportunities for musicians to share their work with the public.

Lastly, don't forget to keep an eye on local event calendars and social media groups dedicated to music in your area. You can also ask friends, coworkers, or fellow music enthusiasts for recommendations on where to find great live music in your community!
- Correct: `False`; F1: `0.000`; evidence hit: `False`
