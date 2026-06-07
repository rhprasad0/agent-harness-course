#!/usr/bin/env python3
"""Generate local APE-style prompt candidates from compact dev stats via Ollama."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:11434"
MODEL = "mistral:7b-instruct-q4_K_M"
OUT_RAW = Path("labs/prompt/results/2026-06-07-local-ape-candidate-generation-raw.md")
OUT_DIR = Path("labs/prompt/prompts")

prompt = """We are optimizing an instruction prompt for a local 7B model solving GSM8K grade-school math word problems.

Baseline prompt scored 8/30 on dev rows. It usually obeys the required final marker, but it often fails by:
- misreading what the question asks for,
- using the wrong quantity or base for percentages,
- doing arithmetic without checking it,
- confusing totals, remaining amounts, profit, and rates.

Write exactly three improved prompt templates for the solver model.
Rules:
- Each template must include the literal placeholder {question} exactly once.
- Each template must require the final output line exactly as: FINAL_ANSWER: <number>
- Do not include row numbers or solve specific examples.
- Do not write placeholders like <prompt template>.

Format your answer exactly like this, but with real prompt text:
CANDIDATE_1_NAME: name
CANDIDATE_1_PROMPT:
real prompt text here with {question}
END_CANDIDATE_1

CANDIDATE_2_NAME: name
CANDIDATE_2_PROMPT:
real prompt text here with {question}
END_CANDIDATE_2

CANDIDATE_3_NAME: name
CANDIDATE_3_PROMPT:
real prompt text here with {question}
END_CANDIDATE_3
"""

payload = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.9, "num_predict": 2200}}
req = urllib.request.Request(
    f"{BASE_URL}/api/generate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=300) as resp:
    data = json.loads(resp.read().decode("utf-8"))
text = data.get("response", "")
OUT_RAW.write_text(text + "\n", encoding="utf-8")
print(f"wrote {OUT_RAW}")

pattern = re.compile(r"CANDIDATE_(\d+)_NAME:\s*([^\n]+)\nCANDIDATE_\1_PROMPT:\n([\s\S]*?)\nEND_CANDIDATE_\1", re.M)
blocks = pattern.findall(text)
if not blocks:
    raise SystemExit("No candidate blocks parsed from local optimizer output")
for num, name, body in blocks[:3]:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower()).strip("_") or f"candidate_{num}"
    path = OUT_DIR / f"ape_local_{num}_{slug}.txt"
    if "{question}" not in body:
        body = body.rstrip() + "\n\nQuestion:\n{question}\n"
    path.write_text(body.strip() + "\n", encoding="utf-8")
    print(f"wrote {path}")
