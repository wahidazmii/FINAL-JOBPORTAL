"""AI service: resume parsing, match scoring, salary prediction."""
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-4o-mini"


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


def _new_chat(system: str) -> LlmChat:
    if not EMERGENT_LLM_KEY:
        raise RuntimeError("EMERGENT_LLM_KEY not configured")
    return LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"tv-{uuid.uuid4()}",
        system_message=system,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)


# ---------- Resume parsing ----------
RESUME_SYSTEM = """Anda adalah AI parser resume untuk platform lowongan kerja Indonesia (Talentiv Jobs).
Tugas: ekstrak data terstruktur dari teks resume.
Balas HANYA JSON valid (tanpa markdown fences) dengan skema TEPAT berikut:
{
  "name": string,
  "email": string | null,
  "phone": string | null,
  "location": string | null,
  "headline": string | null,
  "summary": string | null,
  "skills": string[],
  "experience": [ { "title": string, "company": string, "start": string | null, "end": string | null, "description": string | null } ],
  "education": [ { "degree": string, "institution": string, "start": string | null, "end": string | null, "gpa": string | null } ]
}
Skills harus array string ringkas (nama teknologi/skill saja).
"""


async def parse_resume_text(text: str) -> Dict[str, Any]:
    chat = _new_chat(RESUME_SYSTEM)
    resp = await chat.send_message(UserMessage(text=f"Parse resume berikut:\n\n{text[:8000]}"))
    data = extract_json(resp)
    # Ensure required fields
    data.setdefault("skills", [])
    data.setdefault("experience", [])
    data.setdefault("education", [])
    return data


# ---------- Match score ----------
MATCH_SYSTEM = """Anda adalah AI penilai kecocokan kandidat-lowongan pekerjaan.
Balas HANYA JSON valid (tanpa markdown) dengan skema TEPAT:
{
  "score": integer (0-100),
  "rationale": string (2-3 kalimat Bahasa Indonesia),
  "matched_skills": string[],
  "missing_skills": string[],
  "recommendation": "strong_match" | "good_match" | "weak_match" | "no_match"
}
Skor tinggi (80+) hanya jika >=70% skill wajib terpenuhi dan pengalaman sesuai.
"""


async def match_score(
    candidate_skills: List[str],
    candidate_years: int,
    job_title: str,
    job_required_skills: List[str],
    job_description: Optional[str] = None,
    job_min_years: int = 0,
) -> Dict[str, Any]:
    chat = _new_chat(MATCH_SYSTEM)
    payload = {
        "candidate": {"skills": candidate_skills, "years_experience": candidate_years},
        "job": {
            "title": job_title,
            "required_skills": job_required_skills,
            "min_years": job_min_years,
            "description": (job_description or "")[:1000],
        },
    }
    resp = await chat.send_message(
        UserMessage(text=f"Hitung match score untuk data berikut:\n{json.dumps(payload, ensure_ascii=False)}")
    )
    data = extract_json(resp)
    data.setdefault("matched_skills", [])
    data.setdefault("missing_skills", [])
    data.setdefault("recommendation", "weak_match")
    data.setdefault("rationale", "")
    if not isinstance(data.get("score"), int):
        try:
            data["score"] = int(float(data.get("score", 0)))
        except Exception:
            data["score"] = 0
    data["score"] = max(0, min(100, data["score"]))
    return data


# ---------- Salary prediction ----------
SALARY_SYSTEM = """Anda adalah AI konsultan gaji untuk pasar kerja Indonesia.
Balas HANYA JSON valid (tanpa markdown) dengan skema TEPAT:
{
  "salary_min": integer (IDR/bulan),
  "salary_max": integer (IDR/bulan),
  "currency": "IDR",
  "period": "month",
  "rationale": string (2-3 kalimat Bahasa Indonesia),
  "confidence": "low" | "medium" | "high",
  "assumptions": string[]
}
Gunakan data pasar Indonesia 2024-2025. Rentang harus realistis (min < max, keduanya > 0).
Contoh: Senior Engineer di Jakarta (5+ thn) ~ 20-45 juta/bulan. Fresh graduate ~ 5-10 juta.
"""


async def predict_salary(
    title: str, location: str, years_experience: int = 0, level: str = "mid", skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    chat = _new_chat(SALARY_SYSTEM)
    query = {
        "title": title,
        "location": location,
        "years_experience": years_experience,
        "level": level,
        "skills": skills or [],
    }
    resp = await chat.send_message(
        UserMessage(text=f"Prediksi gaji untuk:\n{json.dumps(query, ensure_ascii=False)}")
    )
    data = extract_json(resp)
    data.setdefault("currency", "IDR")
    data.setdefault("period", "month")
    data.setdefault("assumptions", [])
    data.setdefault("confidence", "medium")
    data.setdefault("rationale", "")
    for k in ("salary_min", "salary_max"):
        if not isinstance(data.get(k), int):
            try:
                data[k] = int(float(data.get(k, 0)))
            except Exception:
                data[k] = 0
    return data
