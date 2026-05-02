"""AI service menggunakan OpenRouter (pengganti Emergent LLM)."""
import json
import os
import re
import httpx  # async version of requests
from typing import Any, Dict, List, Optional

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "z-ai/glm-5-turbo"  # atau model lain di OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def extract_json(raw: str) -> Any:
    if not raw:
        raise ValueError("Empty LLM output")
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found: {raw[:300]}")
    return json.loads(match.group(1))


async def _call_llm(system: str, user: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not configured")
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ---- Resume parsing, match score, salary prediction tetap sama ----
# (salin fungsi parse_resume_text, match_score, predict_salary
#  dari file asli — hanya ganti _new_chat(...).send_message(...)
#  menjadi await _call_llm(SYSTEM_PROMPT, user_message))
