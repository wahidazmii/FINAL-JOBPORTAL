"""
Phase 1 POC: Core AI Features for Talentiv Jobs
Tests 3 critical AI flows in isolation before building the full app.

Tests:
1. Resume Parsing: resume text -> structured JSON (profile)
2. Job Matching: candidate + job -> match score with rationale
3. Salary Prediction: role+location+experience -> salary range (IDR)
"""
import asyncio
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load env from backend
ROOT = Path(__file__).parent
load_dotenv(ROOT / "backend" / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-4o-mini"  # cost-efficient, strong JSON output


# ---------- Helpers ----------
def extract_json(raw: str) -> Any:
    """Extract first JSON object/array from LLM output (tolerant to ```json fences)."""
    if raw is None:
        raise ValueError("Empty LLM output")
    # Strip fenced code block if present
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    # Find first {...} or [...]
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in output: {raw[:300]}")
    return json.loads(match.group(1))


def new_chat(system_message: str) -> LlmChat:
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"poc-{uuid.uuid4()}",
        system_message=system_message,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)
    return chat


# ---------- Test 1: Resume Parsing ----------
SAMPLE_RESUME = """
Ahmad Wijaya
Email: ahmad.wijaya@example.com | Phone: +62 812-3456-7890
Location: Jakarta, Indonesia

PROFIL SINGKAT
Software Engineer dengan 4 tahun pengalaman membangun aplikasi web full-stack.
Memiliki keahlian kuat di React, TypeScript, Node.js, dan PostgreSQL.

PENGALAMAN KERJA
- Senior Software Engineer, Tokopedia (Jan 2023 - sekarang)
  * Memimpin tim 5 engineer untuk membangun modul checkout baru.
  * Migrasi backend monolith ke microservices dengan NestJS.
- Software Engineer, Gojek (Jul 2020 - Dec 2022)
  * Mengembangkan fitur promo di aplikasi GoFood menggunakan React Native.
  * Meningkatkan performa halaman checkout hingga 35%.

PENDIDIKAN
- S1 Teknik Informatika, Universitas Indonesia, 2016-2020, IPK 3.78

SKILLS
React, TypeScript, Node.js, NestJS, PostgreSQL, MongoDB, AWS, Docker, Kubernetes, GraphQL
"""

RESUME_SYSTEM = """Anda adalah AI parser resume untuk platform lowongan kerja Indonesia (Talentiv Jobs).
Tugas Anda: ekstrak data terstruktur dari teks resume.
Balas HANYA dalam JSON valid (tanpa penjelasan, tanpa markdown fences) dengan skema TEPAT berikut:
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
Pastikan skills adalah array string ringkas (nama teknologi/skill saja).
"""


async def test_resume_parsing() -> bool:
    print("\n=== TEST 1: Resume Parsing ===")
    chat = new_chat(RESUME_SYSTEM)
    resp = await chat.send_message(
        UserMessage(text=f"Parse resume berikut:\n\n{SAMPLE_RESUME}")
    )
    try:
        data = extract_json(resp)
    except Exception as e:
        print(f"FAIL - cannot parse JSON: {e}\nRaw: {resp[:400]}")
        return False

    required = ["name", "email", "skills", "experience", "education"]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"FAIL - missing keys: {missing}")
        return False
    if not isinstance(data["skills"], list) or len(data["skills"]) < 3:
        print(f"FAIL - skills too small: {data.get('skills')}")
        return False
    if not isinstance(data["experience"], list) or len(data["experience"]) < 1:
        print("FAIL - experience missing")
        return False
    if "ahmad" not in str(data.get("name", "")).lower():
        print(f"FAIL - wrong name: {data.get('name')}")
        return False
    print(f"PASS - name={data['name']}, skills={len(data['skills'])}, exp={len(data['experience'])}")
    print(f"  Email: {data.get('email')}, Skills sample: {data['skills'][:5]}")
    return True


# ---------- Test 2: Job Matching ----------
CANDIDATE_SKILLS = [
    "React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "GraphQL", "AWS",
]
CANDIDATE_EXPERIENCE_YEARS = 4

JOB_REQUIREMENTS = {
    "title": "Senior Frontend Engineer",
    "required_skills": ["React", "TypeScript", "Next.js", "GraphQL", "Tailwind CSS"],
    "nice_to_have": ["Node.js", "AWS"],
    "min_years": 3,
    "description": "Membangun aplikasi e-commerce modern dengan React + Next.js",
}

MATCH_SYSTEM = """Anda adalah AI penilai kecocokan kandidat-lowongan pekerjaan.
Balas HANYA dalam JSON valid (tanpa markdown/fence) dengan skema TEPAT:
{
  "score": integer (0-100),
  "rationale": string (2-3 kalimat, Bahasa Indonesia),
  "matched_skills": string[],
  "missing_skills": string[],
  "recommendation": "strong_match" | "good_match" | "weak_match" | "no_match"
}
Skor tinggi (80+) hanya jika >=70% skill wajib terpenuhi dan pengalaman sesuai.
"""


async def test_job_match() -> bool:
    print("\n=== TEST 2: Job Matching ===")
    chat = new_chat(MATCH_SYSTEM)
    payload = {
        "candidate": {
            "skills": CANDIDATE_SKILLS,
            "years_experience": CANDIDATE_EXPERIENCE_YEARS,
        },
        "job": JOB_REQUIREMENTS,
    }
    resp = await chat.send_message(
        UserMessage(text=f"Hitung match score untuk data berikut:\n{json.dumps(payload, ensure_ascii=False)}")
    )
    try:
        data = extract_json(resp)
    except Exception as e:
        print(f"FAIL - cannot parse JSON: {e}\nRaw: {resp[:400]}")
        return False

    if not isinstance(data.get("score"), int):
        print(f"FAIL - score not int: {data.get('score')}")
        return False
    if not (0 <= data["score"] <= 100):
        print(f"FAIL - score out of range: {data['score']}")
        return False
    for key in ["rationale", "matched_skills", "missing_skills", "recommendation"]:
        if key not in data:
            print(f"FAIL - missing key {key}")
            return False
    if data["recommendation"] not in ["strong_match", "good_match", "weak_match", "no_match"]:
        print(f"FAIL - bad recommendation: {data['recommendation']}")
        return False
    # Sanity: "React" and "TypeScript" should be in matched_skills
    matched_lower = [s.lower() for s in data["matched_skills"]]
    if "react" not in matched_lower:
        print(f"FAIL - React should match. matched={data['matched_skills']}")
        return False
    print(f"PASS - score={data['score']}, rec={data['recommendation']}")
    print(f"  Matched: {data['matched_skills']}")
    print(f"  Missing: {data['missing_skills']}")
    print(f"  Rationale: {data['rationale'][:150]}")
    return True


# ---------- Test 3: Salary Prediction ----------
SALARY_SYSTEM = """Anda adalah AI konsultan gaji untuk pasar kerja Indonesia.
Balas HANYA JSON valid (tanpa markdown/fence) dengan skema TEPAT:
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
Untuk Senior Engineer di Jakarta pengalaman 5+ tahun, rentang umum 20-45 juta/bulan.
"""


async def test_salary_prediction() -> bool:
    print("\n=== TEST 3: Salary Prediction ===")
    chat = new_chat(SALARY_SYSTEM)
    query = {
        "title": "Senior Frontend Engineer",
        "location": "Jakarta, Indonesia",
        "years_experience": 5,
        "level": "senior",
        "skills": ["React", "TypeScript", "Next.js"],
    }
    resp = await chat.send_message(
        UserMessage(text=f"Prediksi gaji untuk:\n{json.dumps(query, ensure_ascii=False)}")
    )
    try:
        data = extract_json(resp)
    except Exception as e:
        print(f"FAIL - cannot parse JSON: {e}\nRaw: {resp[:400]}")
        return False

    smin = data.get("salary_min")
    smax = data.get("salary_max")
    if not isinstance(smin, int) or not isinstance(smax, int):
        print(f"FAIL - salary not int: min={smin} max={smax}")
        return False
    if smin <= 0 or smax <= smin:
        print(f"FAIL - invalid range: min={smin} max={smax}")
        return False
    # Sanity check: Senior in Jakarta should be at least 10M IDR
    if smax < 10_000_000:
        print(f"FAIL - salary too low for senior: {smax}")
        return False
    if data.get("currency") != "IDR":
        print(f"FAIL - wrong currency: {data.get('currency')}")
        return False
    if data.get("confidence") not in ["low", "medium", "high"]:
        print(f"FAIL - bad confidence: {data.get('confidence')}")
        return False
    print(f"PASS - {smin:,} - {smax:,} IDR/bulan (conf={data['confidence']})")
    print(f"  Rationale: {data['rationale'][:150]}")
    return True


# ---------- Runner ----------
async def main():
    if not EMERGENT_LLM_KEY:
        print("ERROR: EMERGENT_LLM_KEY not set")
        sys.exit(1)
    print(f"Using model: {MODEL_PROVIDER}/{MODEL_NAME}")

    results = []
    results.append(("Resume Parsing", await test_resume_parsing()))
    results.append(("Job Matching", await test_job_match()))
    results.append(("Salary Prediction", await test_salary_prediction()))

    print("\n" + "=" * 50)
    print("POC SUMMARY")
    print("=" * 50)
    all_passed = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            all_passed = False
    print("=" * 50)
    if not all_passed:
        print("ONE OR MORE TESTS FAILED - FIX BEFORE BUILDING APP")
        sys.exit(1)
    print("ALL TESTS PASSED - CORE AI READY")


if __name__ == "__main__":
    asyncio.run(main())
