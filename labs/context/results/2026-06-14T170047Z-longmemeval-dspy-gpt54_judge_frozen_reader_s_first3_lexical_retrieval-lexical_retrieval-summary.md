# LongMemEval DSPy Run Summary

Run ID: `2026-06-14T170047Z`
Condition: `gpt54_judge_frozen_reader_s_first3_lexical_retrieval`
Dataset: `labs/context/data/longmemeval/longmemeval_s_cleaned.json`
Model: `ollama_chat/llama3:latest`
Context policy: `lexical_retrieval`
Judge provider/model: `codex-bridge` / `gpt-5.4`
Limit / offset / repeats: `3` / `0` / `5`

## Aggregate

| Policy | Rows | Questions | Repeats | GPT-4o judge acc | Judge errors | Heuristic acc | Mean F1 | Recall any@3 | Recall all@3 | NDCG any@3 | MRR | SGI | Parse errors | Mean context words | Mean elapsed sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lexical_retrieval | 15 | 3 | 5 | 0.000 | 0 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.333 | n/a | 0 | 1965.3 | 3.18 |

## Notes

- Headline QA accuracy is GPT-4o judge accuracy when `--judge-provider codex-bridge --judge-model gpt-4o` succeeds.
- Local heuristic correctness and token F1 are diagnostics, not official LongMemEval scoring.
- Embedding semantic grounding is diagnostic and not an official LongMemEval score.
- Official-compatible per-repeat hypothesis JSONL files are written for audit/re-evaluation.
- DSPy/LiteLLM does not expose Ollama `prompt_eval_count` here, so the summary reports context words/chars instead.

## Row sample

### e47becba repeat 1

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `False`

### 118b2229 repeat 1

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I think I can help you with that! Since you're interested in exploring more of the singer-songwriter and Americana genres, I'd recommend checking out local music venues and festivals that feature these types of artists. You could also look into local open mic nights or songwriting circles where you might discover new talent.

Additionally, consider reaching out to local music organizations or radio stations that focus on indie-folk or Americana music. They might have recommendations for upcoming shows or events in your area.

Lastly, don't forget to keep an eye on social media and online event calendars to stay up-to-date on local concerts and festivals.
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `False`

### 51a45a95 repeat 1

- Type: `single-session-user`
- Question: Where did I redeem a $5 coupon on coffee creamer?
- Gold: Target
- Pred: I don't know
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `True`

### e47becba repeat 2

- Type: `single-session-user`
- Question: What degree did I graduate with?
- Gold: Business Administration
- Pred: I don't know
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `False`

### 118b2229 repeat 2

- Type: `single-session-user`
- Question: How long is my daily commute to work?
- Gold: 45 minutes each way
- Pred: I think I can help you with that! Since you're interested in exploring more of the singer-songwriter and Americana genres, I'd recommend checking out local music venues and festivals that feature these types of artists. You could also look into attending open mic nights or songwriting workshops in your area to meet other musicians and learn about new talent.

Additionally, consider following local music blogs, social media groups, or online forums dedicated to music in your community. These can be great resources for discovering new artists, staying up-to-date on upcoming shows, and connecting with fellow music enthusiasts.

Lastly, don't forget to support local music by attending concerts and buying merchandise from your favorite artists when possible!
- GPT-4o judge correct: `False`; judge error: ``
- Heuristic correct: `False`; F1: `0.000`; evidence hit: `False`
