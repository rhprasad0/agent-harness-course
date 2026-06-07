# GSM8K Prompt Template Evaluation

- Date: 2026-06-07T145319Z
- Prompt ID: `ape_hybrid_quantity_checklist`
- Prompt template: `labs/prompt/prompts/ape_hybrid_quantity_checklist.txt`
- Model: `mistral:7b-instruct-q4_K_M` via Ollama `http://127.0.0.1:11434`
- Dataset: `labs/prompt/data/gsm8k/test.jsonl`
- Slice: offset 0, limit 30
- Temperature: 0.0
- Generation budget: num_predict=256
- Result: 8/30 correct (26.7%)
- Average elapsed: 1.91s/question
- Average prompt tokens reported by Ollama: 213.4
- Average completion tokens reported by Ollama: 238.4

## Parse statuses

| Status | Count |
|---|---:|
| `final_answer_marker` | 12 |
| `last_number_fallback` | 18 |

## Per-question results

| Row | Correct | Pred | Gold | Parse status | Question |
|---:|:---:|---:|---:|---|---|
| 1 | ✅ | 18 | 18 | `final_answer_marker` | Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every... |
| 2 | ✅ | 3 | 3 | `final_answer_marker` | A robe takes 2 bolts of blue fiber and half that much white fiber.  How many bolts in total does it take? |
| 3 | ❌ | 19500 | 70000 | `last_number_fallback` | Josh decides to try flipping a house.  He buys a house for $80,000 and then puts in $50,000 in repairs.  This increas... |
| 4 | ✅ | 540 | 540 | `final_answer_marker` | James decides to run 3 sprints 3 times a week.  He runs 60 meters each sprint.  How many total meters does he run a w... |
| 5 | ❌ | 1 | 20 | `final_answer_marker` | Every day, Wendi feeds each of her chickens three cups of mixed chicken feed, containing seeds, mealworms and vegetab... |
| 6 | ❌ | 3 | 64 | `last_number_fallback` | Kylar went to the store to buy glasses for his new apartment. One glass costs $5, but every second glass costs only 6... |
| 7 | ❌ | 20 | 260 | `last_number_fallback` | Toulouse has twice as many sheep as Charleston. Charleston has 4 times as many sheep as Seattle. How many sheep do To... |
| 8 | ❌ | 1.68 | 160 | `last_number_fallback` | Carla is downloading a 200 GB file. Normally she can download 2 GB/minute, but 40% of the way through the download, W... |
| 9 | ❌ | 1.5 | 45 | `last_number_fallback` | John drives for 3 hours at a speed of 60 mph and then turns around because he realizes he forgot something very impor... |
| 10 | ❌ | 40 | 460 | `last_number_fallback` | Eliza's rate per hour for the first 40 hours she works each week is $10. She also receives an overtime pay of 1.2 tim... |
| 11 | ❌ | 126 | 366 | `last_number_fallback` | A new program had 60 downloads in the first month. The number of downloads in the second month was three times as man... |
| 12 | ❌ | 204 | 694 | `final_answer_marker` | Toula went to the bakery and bought various types of pastries. She bought 3 dozen donuts which cost $68 per dozen, 2 ... |
| 13 | ❌ | 9.5 | 13 | `last_number_fallback` | Carlos is planting a lemon tree. The tree will cost $90 to plant. Each year it will grow 7 lemons, which he can sell ... |
| 14 | ❌ | 1 | 18 | `last_number_fallback` | Melanie is a door-to-door saleswoman. She sold a third of her vacuum cleaners at the green house, 2 more to the red h... |
| 15 | ❌ | 3 | 60 | `last_number_fallback` | In a dance class of 20 students, 20% enrolled in contemporary dance, 25% of the remaining enrolled in jazz dance, and... |
| 16 | ❌ | 750 | 125 | `last_number_fallback` | A merchant wants to make a choice of purchase between 2 purchase plans: jewelry worth $5,000 or electronic gadgets wo... |
| 17 | ✅ | 230 | 230 | `final_answer_marker` | Two trains leave San Rafael at the same time. They begin traveling westward, both traveling for 80 miles. The next da... |
| 18 | ❌ | 1150 | 57500 | `last_number_fallback` | Jill gets paid $20 per hour to teach and $30 to be a cheerleading coach. If she works 50 weeks a year, 35 hours a wee... |
| 19 | ❌ | 4 | 7 | `final_answer_marker` | Claire makes a 3 egg omelet every morning for breakfast.  How many dozens of eggs will she eat in 4 weeks? |
| 20 | ✅ | 6 | 6 | `last_number_fallback` | Marissa is hiking a 12-mile trail. She took 1 hour to walk the first 4 miles, then another hour to walk the next two ... |
| 21 | ❌ | 15.67 | 15 | `last_number_fallback` | I have 10 liters of orange drink that are two-thirds water and I wish to add it to 15 liters of pineapple drink that ... |
| 22 | ❌ | 31 | 14 | `final_answer_marker` | Raymond and Samantha are cousins. Raymond was born 6 years before Samantha. Raymond had a son at the age of 23. If Sa... |
| 23 | ❌ | 5 | 7 | `final_answer_marker` | Billy sells DVDs. He has 8 customers on Tuesday. His first 3 customers buy one DVD each.  His next 2 customers buy 2 ... |
| 24 | ❌ | -10 | 8 | `final_answer_marker` | A candle melts by 2 centimeters every hour that it burns. How many centimeters shorter will a candle be after burning... |
| 25 | ✅ | 26 | 26 | `final_answer_marker` | Kyle bought last year's best-selling book for $19.50. This is with a 25% discount from the original price. What was t... |
| 26 | ✅ | 2 | 2 | `final_answer_marker` | Marie ordered one chicken meal that costs $12, 5 packs of milk that costs $3 each, 4 apples that cost $1.50 each, and... |
| 27 | ❌ | 12 | 243 | `last_number_fallback` | Mishka bought 3 pairs of shorts, 3 pairs of pants, and 3 pairs of shoes. One pair of shorts costs $16.50. One pair of... |
| 28 | ✅ | 16 | 16 | `last_number_fallback` | Cynthia eats one serving of ice cream every night.  She buys cartons of ice cream with 15 servings of ice cream per c... |
| 29 | ❌ | 45 | 25 | `last_number_fallback` | Henry made two stops during his 60-mile bike trip. He first stopped after 20 miles. His second stop was 15 miles befo... |
| 30 | ❌ | 66 | 104 | `last_number_fallback` | Gloria is shoe shopping when she comes across a pair of boots that fit her shoe budget. However, she has to choose be... |

## Notes

This evaluator intentionally does not generate or optimize prompts. It only scores a supplied prompt template so APE, OPRO, and GEPA candidates can be compared through the same harness.
Raw JSONL: `labs/prompt/results/2026-06-07T145319Z-gsm8k-test-offset0-limit30-ollama-mistral-7b-instruct-q4_K_M-prompt-ape_hybrid_quantity_checklist.jsonl`
