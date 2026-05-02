"""Talentiv Jobs - FastAPI backend entrypoint."""
from __future__ import annotations

import base64
import io
import logging
import os
from pathlib import Path
from typing import List, Optional

import pdfplumber
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from slugify import slugify
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from auth import (  # noqa: E402
    create_token,
    get_current_user,
    get_current_user_optional,
    hash_password,
    require_role,
    verify_password,
)
from ai_service import match_score, parse_resume_text, predict_salary  # noqa: E402
from rate_limit import rate_limit  # noqa: E402
from admin_routes import build_admin_router  # noqa: E402
from embeddings import (  # noqa: E402
    cosine_similarity,
    embed_text,
    job_text,
    profile_text,
    query_text,
)
from cache_utils import (  # noqa: E402
    categories_cache,
    featured_jobs_cache,
    make_key,
    match_cache,
    salary_cache,
)
from models import (  # noqa: E402
    Application,
    ApplicationInput,
    ApplicationStatusUpdate,
    AuthResponse,
    Category,
    Company,
    CompanyInput,
    Job,
    JobInput,
    LoginInput,
    MatchScoreInput,
    Profile,
    ProfileUpdateInput,
    RegisterInput,
    ResumeParseInput,
    SalaryPredictionInput,
    SavedJob,
    UserInDB,
    UserPublic,
    new_id,
    now_iso,
)
from seed import seed_database  # noqa: E402

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# Env config
ENV = os.environ.get("ENV", "development").lower()
ENABLE_DEMO_SEED = os.environ.get("ENABLE_DEMO_SEED", "true").lower() == "true"
ENABLE_DEMO_USERS = os.environ.get("ENABLE_DEMO_USERS", "true").lower() == "true"

app = FastAPI(title="Talentiv Jobs API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("talentiv")


# ---------- Helpers ----------
def clean_doc(doc: Optional[dict]) -> Optional[dict]:
    if doc is None:
        return None
    doc.pop("_id", None)
    return doc


async def get_user_by_id(user_id: str) -> Optional[dict]:
    return clean_doc(await db.users.find_one({"id": user_id}))


async def ensure_profile(user_id: str) -> dict:
    prof = await db.profiles.find_one({"user_id": user_id})
    if not prof:
        new = Profile(user_id=user_id).model_dump()
        await db.profiles.insert_one(new)
        return new
    return clean_doc(prof) or {}


async def unique_slug(base: str, collection, extra_filter: Optional[dict] = None) -> str:
    base_slug = slugify(base)[:80] or f"item-{new_id()[:8]}"
    candidate = base_slug
    i = 1
    while await collection.find_one({"slug": candidate, **(extra_filter or {})}):
        i += 1
        candidate = f"{base_slug}-{i}"
    return candidate


def user_public(doc: dict) -> UserPublic:
    return UserPublic(
        id=doc["id"],
        email=doc["email"],
        name=doc["name"],
        role=doc["role"],
        created_at=doc["created_at"],
    )


# ---------- Root ----------
@api_router.get("/")
async def root():
    return {"message": "Talentiv Jobs API", "status": "ok"}


@api_router.get("/health")
async def health():
    return {"status": "ok"}


# ---------- Auth ----------
@api_router.post("/auth/register", response_model=AuthResponse)
async def register(data: RegisterInput):
    if data.role == "admin":
        raise HTTPException(status_code=403, detail="Admin tidak dapat mendaftar via publik")
    existing = await db.users.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if data.role == "employer" and not data.company_name:
        raise HTTPException(status_code=400, detail="Nama perusahaan wajib untuk employer")

    user = UserInDB(
        id=new_id(),
        email=data.email.lower(),
        name=data.name,
        role=data.role,
        password_hash=hash_password(data.password),
        created_at=now_iso(),
    )
    doc = user.model_dump()

    # Create company for employer
    if data.role == "employer" and data.company_name:
        slug = await unique_slug(data.company_name, db.companies)
        company = Company(
            owner_id=user.id,
            name=data.company_name,
            slug=slug,
            location="Indonesia",
        )
        await db.companies.insert_one(company.model_dump())
        doc["company_id"] = company.id

    await db.users.insert_one(doc)

    # Ensure candidate profile
    if data.role == "candidate":
        await ensure_profile(user.id)

    token = create_token(user.id, user.role)
    return AuthResponse(token=token, user=user_public(doc))


@api_router.post("/auth/login", response_model=AuthResponse)
async def login(data: LoginInput):
    user = await db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    if user.get("is_disabled"):
        raise HTTPException(status_code=403, detail="Akun dinonaktifkan. Hubungi admin.")
    token = create_token(user["id"], user["role"])
    return AuthResponse(token=token, user=user_public(user))


@api_router.get("/auth/me")
async def me(current: dict = Depends(get_current_user)):
    user = await get_user_by_id(current["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    profile = None
    company = None
    if user["role"] == "candidate":
        profile = await ensure_profile(user["id"])
    if user["role"] == "employer" and user.get("company_id"):
        company = clean_doc(await db.companies.find_one({"id": user["company_id"]}))
    return {"user": user_public(user).model_dump(), "profile": profile, "company": company}


# ---------- Categories ----------
@api_router.get("/categories", response_model=List[Category])
async def list_categories():
    cached = categories_cache.get("all")
    if cached is not None:
        return cached
    cats = await db.categories.find({}, {"_id": 0}).sort("order_rank", 1).to_list(100)
    for c in cats:
        c["job_count"] = await db.jobs.count_documents({"category_id": c["id"], "status": "published"})
    categories_cache["all"] = cats
    return cats


# ---------- Companies ----------
@api_router.get("/companies/{company_id}")
async def get_company(company_id: str):
    company = clean_doc(await db.companies.find_one({"$or": [{"id": company_id}, {"slug": company_id}]}))
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")
    # Include active jobs
    jobs = await db.jobs.find({"company_id": company["id"], "status": "published"}, {"_id": 0}).to_list(100)
    return {"company": company, "jobs": jobs}


@api_router.put("/companies/me")
async def update_my_company(
    data: CompanyInput, current: dict = Depends(require_role("employer"))
):
    user = await get_user_by_id(current["sub"])
    if not user or not user.get("company_id"):
        raise HTTPException(status_code=404, detail="Company not found")
    update = data.model_dump(exclude_unset=True)
    await db.companies.update_one({"id": user["company_id"]}, {"$set": update})
    company = clean_doc(await db.companies.find_one({"id": user["company_id"]}))
    return company


# ---------- Jobs ----------
async def _enrich_job(job: dict) -> dict:
    company = clean_doc(await db.companies.find_one({"id": job["company_id"]})) or {}
    return {
        "id": job["id"],
        "title": job["title"],
        "slug": job["slug"],
        "description": job.get("description", ""),
        "requirements": job.get("requirements", ""),
        "skills": job.get("skills", []),
        "employment_type": job.get("employment_type", "full_time"),
        "work_mode": job.get("work_mode", "onsite"),
        "experience_level": job.get("experience_level", "mid"),
        "min_years": job.get("min_years", 0),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "currency": job.get("currency", "IDR"),
        "location": job.get("location", ""),
        "category_id": job.get("category_id"),
        "status": job.get("status", "published"),
        "created_at": job.get("created_at"),
        "views": job.get("views", 0),
        "applications_count": job.get("applications_count", 0),
        "is_featured": job.get("is_featured", False),
        "company": {
            "id": company.get("id"),
            "name": company.get("name"),
            "logo_url": company.get("logo_url"),
            "location": company.get("location"),
            "slug": company.get("slug"),
        },
    }


@api_router.get("/jobs")
async def list_jobs(
    q: Optional[str] = None,
    location: Optional[str] = None,
    employment_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    experience_level: Optional[str] = None,
    category_id: Optional[str] = None,
    salary_min: Optional[int] = None,
    sort: Optional[str] = None,  # "newest" (default) | "relevance" | "salary"
    page: int = 1,
    page_size: int = 12,
):
    filters: dict = {"status": "published"}
    if q:
        filters["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"skills": {"$regex": q, "$options": "i"}},
        ]
    if location and location.lower() != "semua":
        filters["location"] = {"$regex": location, "$options": "i"}
    if employment_type:
        filters["employment_type"] = employment_type
    if work_mode:
        filters["work_mode"] = work_mode
    if experience_level:
        filters["experience_level"] = experience_level
    if category_id:
        filters["category_id"] = category_id
    if salary_min:
        filters["salary_max"] = {"$gte": salary_min}

    total = await db.jobs.count_documents(filters)

    # --- Semantic relevance sort ---
    if sort == "relevance" and q:
        # Fetch candidate pool (cap to keep fast)
        pool = await db.jobs.find(filters, {"_id": 0}).limit(200).to_list(200)
        try:
            q_vec = embed_text(query_text(q, location))
            scored = []
            for j in pool:
                vec = j.get("embedding")
                if not vec:
                    vec = embed_text(job_text(j))
                    # best-effort backfill (fire-and-forget)
                    await db.jobs.update_one({"id": j["id"]}, {"$set": {"embedding": vec}})
                    j["embedding"] = vec
                s = cosine_similarity(q_vec, vec)
                scored.append((s, j))
            scored.sort(key=lambda x: x[0], reverse=True)
            start = max(0, (page - 1) * page_size)
            page_items = [j for _, j in scored[start:start + page_size]]
            items = []
            for j in page_items:
                enriched = await _enrich_job(j)
                # expose relevance 0-100 for UI
                enriched["relevance_score"] = int(round(max(0.0, min(1.0, next(s for s, x in scored if x["id"] == j["id"]))) * 100))
                items.append(enriched)
            return {"items": items, "total": len(scored), "page": page, "page_size": page_size, "sort": "relevance"}
        except Exception as e:
            logger.warning("Relevance sort fallback to newest: %s", e)

    # --- Default: newest ---
    skip = max(0, (page - 1) * page_size)
    sort_key = [("created_at", -1)]
    if sort == "salary":
        sort_key = [("salary_max", -1), ("created_at", -1)]
    cursor = db.jobs.find(filters, {"_id": 0}).sort(sort_key).skip(skip).limit(page_size)
    jobs = [await _enrich_job(j) for j in await cursor.to_list(page_size)]
    return {"items": jobs, "total": total, "page": page, "page_size": page_size, "sort": sort or "newest"}


@api_router.get("/jobs/featured")
async def featured_jobs(limit: int = 6):
    key = make_key("featured", limit)
    cached = featured_jobs_cache.get(key)
    if cached is not None:
        return cached
    # First get truly featured jobs, then fill with recent published
    featured_cursor = db.jobs.find({"status": "published", "is_featured": True}, {"_id": 0}).sort("created_at", -1).limit(limit)
    featured_list = await featured_cursor.to_list(limit)
    if len(featured_list) < limit:
        featured_ids = {j["id"] for j in featured_list}
        remaining = limit - len(featured_list)
        recent_cursor = db.jobs.find(
            {"status": "published", "id": {"$nin": list(featured_ids)}},
            {"_id": 0}
        ).sort("created_at", -1).limit(remaining)
        recent = await recent_cursor.to_list(remaining)
        featured_list.extend(recent)
    jobs = [await _enrich_job(j) for j in featured_list]
    featured_jobs_cache[key] = jobs
    return jobs


@api_router.get("/jobs/{slug}")
async def get_job(slug: str):
    job = clean_doc(await db.jobs.find_one({"$or": [{"slug": slug}, {"id": slug}]}))
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    # Increment view (best-effort)
    await db.jobs.update_one({"id": job["id"]}, {"$inc": {"views": 1}})
    enriched = await _enrich_job(job)

    # Related jobs in same category
    related_filter = {"status": "published", "id": {"$ne": job["id"]}}
    if job.get("category_id"):
        related_filter["category_id"] = job["category_id"]
    related_cursor = db.jobs.find(related_filter, {"_id": 0}).limit(4)
    related = [await _enrich_job(j) for j in await related_cursor.to_list(4)]
    enriched["related"] = related
    return enriched


@api_router.post("/jobs")
async def create_job(data: JobInput, current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    if not user or not user.get("company_id"):
        raise HTTPException(status_code=400, detail="Lengkapi profil perusahaan dulu")
    slug = await unique_slug(data.title, db.jobs)
    job = Job(
        company_id=user["company_id"],
        slug=slug,
        **data.model_dump(),
    )
    doc = job.model_dump()
    # Compute embedding (best-effort)
    try:
        doc["embedding"] = embed_text(job_text(doc))
    except Exception as e:
        logger.warning("Embedding failed on create: %s", e)
        doc["embedding"] = None
    await db.jobs.insert_one(doc)
    featured_jobs_cache.clear()
    categories_cache.clear()
    return await _enrich_job(doc)


@api_router.put("/jobs/{job_id}")
async def update_job(job_id: str, data: JobInput, current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    job = await db.jobs.find_one({"id": job_id})
    if not job or job.get("company_id") != user.get("company_id"):
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    update = data.model_dump(exclude_unset=True)
    # Recompute embedding if any semantic field changed
    semantic_keys = {"title", "description", "requirements", "skills", "location", "experience_level"}
    if any(k in update for k in semantic_keys):
        merged = {**job, **update}
        try:
            update["embedding"] = embed_text(job_text(merged))
        except Exception as e:
            logger.warning("Embedding failed on update: %s", e)
    await db.jobs.update_one({"id": job_id}, {"$set": update})
    featured_jobs_cache.clear()
    return await _enrich_job(clean_doc(await db.jobs.find_one({"id": job_id})))


@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    job = await db.jobs.find_one({"id": job_id})
    if not job or job.get("company_id") != user.get("company_id"):
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    await db.jobs.delete_one({"id": job_id})
    return {"ok": True}


@api_router.get("/employer/jobs")
async def list_my_jobs(current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    cursor = db.jobs.find({"company_id": user.get("company_id")}, {"_id": 0}).sort("created_at", -1)
    jobs = [await _enrich_job(j) for j in await cursor.to_list(500)]
    return jobs


@api_router.get("/employer/stats")
async def employer_stats(current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    company_id = user.get("company_id")
    total_jobs = await db.jobs.count_documents({"company_id": company_id})
    active_jobs = await db.jobs.count_documents({"company_id": company_id, "status": "published"})
    # Applications count via jobs
    job_ids = [j["id"] async for j in db.jobs.find({"company_id": company_id}, {"id": 1})]
    total_apps = await db.applications.count_documents({"job_id": {"$in": job_ids}}) if job_ids else 0
    interview_apps = await db.applications.count_documents(
        {"job_id": {"$in": job_ids}, "status": "interview"}
    ) if job_ids else 0
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_apps,
        "interview_count": interview_apps,
    }


# ---------- Applications ----------
@api_router.post("/applications")
async def apply_job(data: ApplicationInput, current: dict = Depends(require_role("candidate"))):
    job = clean_doc(await db.jobs.find_one({"id": data.job_id}))
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    existing = await db.applications.find_one({"job_id": data.job_id, "candidate_id": current["sub"]})
    if existing:
        raise HTTPException(status_code=400, detail="Anda sudah melamar lowongan ini")

    profile = await ensure_profile(current["sub"])
    skills = profile.get("skills", []) or []
    years = len(profile.get("experience", []) or [])

    # Compute match score using AI (best-effort; fallback to simple overlap)
    match: dict = {}
    try:
        match = await match_score(
            candidate_skills=skills,
            candidate_years=years,
            job_title=job["title"],
            job_required_skills=job.get("skills", []),
            job_description=job.get("description"),
            job_min_years=job.get("min_years", 0),
        )
    except Exception as e:
        logger.warning(f"Match scoring failed, fallback simple: {e}")
        cs_lower = {s.lower() for s in skills}
        rs = job.get("skills", []) or []
        matched = [s for s in rs if s.lower() in cs_lower]
        missing = [s for s in rs if s.lower() not in cs_lower]
        score = int(100 * len(matched) / max(1, len(rs))) if rs else 50
        match = {
            "score": score,
            "rationale": "Skor dihitung secara otomatis berdasarkan kecocokan skill.",
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendation": "good_match" if score >= 70 else "weak_match",
        }

    app_obj = Application(
        job_id=data.job_id,
        candidate_id=current["sub"],
        cover_letter=data.cover_letter,
        match_score=match.get("score"),
        matched_skills=match.get("matched_skills", []),
        missing_skills=match.get("missing_skills", []),
        rationale=match.get("rationale"),
    )
    await db.applications.insert_one(app_obj.model_dump())
    await db.jobs.update_one({"id": data.job_id}, {"$inc": {"applications_count": 1}})
    return app_obj.model_dump()


@api_router.get("/applications/candidate")
async def my_applications(current: dict = Depends(require_role("candidate"))):
    apps = await db.applications.find({"candidate_id": current["sub"]}, {"_id": 0}).sort("created_at", -1).to_list(500)
    # Enrich with job+company summary
    result = []
    for a in apps:
        job = clean_doc(await db.jobs.find_one({"id": a["job_id"]}))
        if not job:
            continue
        enriched_job = await _enrich_job(job)
        result.append({**a, "job": enriched_job})
    return result


@api_router.get("/applications/job/{job_id}")
async def job_applications(job_id: str, current: dict = Depends(require_role("employer"))):
    user = await get_user_by_id(current["sub"])
    job = await db.jobs.find_one({"id": job_id})
    if not job or job.get("company_id") != user.get("company_id"):
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    apps = await db.applications.find({"job_id": job_id}, {"_id": 0}).sort("match_score", -1).to_list(500)
    # Enrich with candidate info
    result = []
    for a in apps:
        cand = await get_user_by_id(a["candidate_id"])
        prof = await db.profiles.find_one({"user_id": a["candidate_id"]}, {"_id": 0})
        result.append(
            {
                **a,
                "candidate": {
                    "id": cand["id"] if cand else a["candidate_id"],
                    "name": cand["name"] if cand else "Unknown",
                    "email": cand["email"] if cand else None,
                    "headline": (prof or {}).get("headline"),
                    "skills": (prof or {}).get("skills", []),
                    "location": (prof or {}).get("location"),
                },
            }
        )
    return result


@api_router.put("/applications/{app_id}/status")
async def update_application_status(
    app_id: str, data: ApplicationStatusUpdate, current: dict = Depends(require_role("employer"))
):
    user = await get_user_by_id(current["sub"])
    app_doc = await db.applications.find_one({"id": app_id})
    if not app_doc:
        raise HTTPException(status_code=404, detail="Aplikasi tidak ditemukan")
    job = await db.jobs.find_one({"id": app_doc["job_id"]})
    if not job or job.get("company_id") != user.get("company_id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.applications.update_one({"id": app_id}, {"$set": {"status": data.status}})
    return clean_doc(await db.applications.find_one({"id": app_id}))


# ---------- Saved Jobs ----------
@api_router.post("/saved/{job_id}")
async def save_job(job_id: str, current: dict = Depends(require_role("candidate"))):
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
    existing = await db.saved_jobs.find_one({"user_id": current["sub"], "job_id": job_id})
    if existing:
        return clean_doc(existing)
    saved = SavedJob(user_id=current["sub"], job_id=job_id)
    await db.saved_jobs.insert_one(saved.model_dump())
    return saved.model_dump()


@api_router.delete("/saved/{job_id}")
async def unsave_job(job_id: str, current: dict = Depends(require_role("candidate"))):
    await db.saved_jobs.delete_one({"user_id": current["sub"], "job_id": job_id})
    return {"ok": True}


@api_router.get("/saved")
async def list_saved(current: dict = Depends(require_role("candidate"))):
    saved = await db.saved_jobs.find({"user_id": current["sub"]}, {"_id": 0}).sort("created_at", -1).to_list(500)
    result = []
    for s in saved:
        job = clean_doc(await db.jobs.find_one({"id": s["job_id"]}))
        if job:
            result.append({**s, "job": await _enrich_job(job)})
    return result


@api_router.get("/saved/check/{job_id}")
async def check_saved(job_id: str, current: dict = Depends(require_role("candidate"))):
    s = await db.saved_jobs.find_one({"user_id": current["sub"], "job_id": job_id})
    return {"saved": bool(s)}


# ---------- Profile ----------
@api_router.get("/profile")
async def get_profile(current: dict = Depends(get_current_user)):
    return await ensure_profile(current["sub"])


@api_router.put("/profile")
async def update_profile(data: ProfileUpdateInput, current: dict = Depends(get_current_user)):
    await ensure_profile(current["sub"])
    # Allow None to be excluded but keep empty lists (user might clear skills intentionally)
    raw = data.model_dump(exclude_unset=True)
    update = {k: v for k, v in raw.items() if v is not None or isinstance(v, list)}
    update["updated_at"] = now_iso()
    await db.profiles.update_one({"user_id": current["sub"]}, {"$set": update})
    return clean_doc(await db.profiles.find_one({"user_id": current["sub"]}))


@api_router.post("/profile/resume")
async def upload_resume(data: ResumeParseInput, current: dict = Depends(require_role("candidate"))):
    """Accept either plain text or base64-encoded PDF. Parse via AI and update profile."""
    resume_text: Optional[str] = None
    if data.text:
        resume_text = data.text
    elif data.pdf_base64:
        try:
            raw = base64.b64decode(data.pdf_base64)
            if len(raw) > 5 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="PDF terlalu besar (max 5MB)")
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            resume_text = "\n\n".join(pages).strip()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gagal membaca PDF: {e}")
    if not resume_text:
        raise HTTPException(status_code=400, detail="Teks resume kosong")

    try:
        parsed = await parse_resume_text(resume_text)
    except Exception as e:
        logger.error(f"Resume parse failed: {e}")
        raise HTTPException(status_code=500, detail="AI parsing gagal, coba lagi")

    await ensure_profile(current["sub"])
    update = {
        "headline": parsed.get("headline"),
        "summary": parsed.get("summary"),
        "location": parsed.get("location"),
        "phone": parsed.get("phone"),
        "skills": parsed.get("skills", []),
        "experience": parsed.get("experience", []),
        "education": parsed.get("education", []),
        "resume_text": resume_text[:20000],
        "updated_at": now_iso(),
    }
    update = {k: v for k, v in update.items() if v is not None}
    await db.profiles.update_one({"user_id": current["sub"]}, {"$set": update})
    profile = clean_doc(await db.profiles.find_one({"user_id": current["sub"]}))
    return {"profile": profile, "parsed": parsed}


# ---------- Candidate dashboard stats ----------
@api_router.get("/candidate/stats")
async def candidate_stats(current: dict = Depends(require_role("candidate"))):
    total_apps = await db.applications.count_documents({"candidate_id": current["sub"]})
    interview = await db.applications.count_documents({"candidate_id": current["sub"], "status": "interview"})
    saved_count = await db.saved_jobs.count_documents({"user_id": current["sub"]})
    return {
        "total_applications": total_apps,
        "interview_count": interview,
        "saved_count": saved_count,
    }


@api_router.get("/candidate/recommendations")
async def candidate_recommendations(current: dict = Depends(require_role("candidate")), limit: int = 6):
    profile = await ensure_profile(current["sub"])
    skills = profile.get("skills", []) or []
    if not skills and not profile.get("summary") and not profile.get("headline"):
        cursor = db.jobs.find({"status": "published"}, {"_id": 0}).sort("created_at", -1).limit(limit)
        jobs = [await _enrich_job(j) for j in await cursor.to_list(limit)]
        return jobs

    # Build candidate embedding from profile
    try:
        cand_vec = embed_text(profile_text(profile))
    except Exception as e:
        logger.warning("Profile embedding failed, falling back to keyword: %s", e)
        cand_vec = None

    pool = await db.jobs.find({"status": "published"}, {"_id": 0}).limit(200).to_list(200)
    cand_skills_lower = {s.lower() for s in skills}

    scored = []
    for j in pool:
        rs = j.get("skills") or []
        matched = [s for s in rs if s.lower() in cand_skills_lower]
        keyword_score = (len(matched) / len(rs)) if rs else 0.0  # 0..1
        sem_score = 0.0
        if cand_vec is not None:
            vec = j.get("embedding")
            if not vec:
                try:
                    vec = embed_text(job_text(j))
                    await db.jobs.update_one({"id": j["id"]}, {"$set": {"embedding": vec}})
                except Exception:
                    vec = None
            if vec:
                sem_score = cosine_similarity(cand_vec, vec)
        # Hybrid: 65% semantic + 35% skill overlap
        final = 0.65 * sem_score + 0.35 * keyword_score
        scored.append((final, sem_score, keyword_score, j, matched))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:limit]
    result = []
    for final, sem, kw, j, matched in top:
        enriched = await _enrich_job(j)
        # Map to 0-100 for UI; rescale slightly so good matches feel right
        enriched["match_score"] = max(0, min(100, int(round(final * 100))))
        enriched["semantic_score"] = round(sem, 3)
        enriched["keyword_score"] = round(kw, 3)
        result.append(enriched)
    return result


# ---------- AI Endpoints ----------
@api_router.post("/ai/parse-resume", dependencies=[Depends(rate_limit(capacity=5, refill_per_sec=0.1))])
async def ai_parse_resume(data: ResumeParseInput, _: Optional[dict] = Depends(get_current_user_optional)):
    if not data.text:
        raise HTTPException(status_code=400, detail="Isi teks resume")
    try:
        return await parse_resume_text(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing gagal: {e}")


@api_router.post("/ai/match-score", dependencies=[Depends(rate_limit(capacity=15, refill_per_sec=0.3))])
async def ai_match_score(data: MatchScoreInput):
    required_skills = data.job_required_skills or []
    job_title = data.job_title or ""
    job_desc = data.job_description
    min_years = data.job_min_years or 0
    if data.job_id:
        job = await db.jobs.find_one({"id": data.job_id})
        if job:
            required_skills = required_skills or job.get("skills", [])
            job_title = job_title or job.get("title", "")
            job_desc = job_desc or job.get("description")
            min_years = min_years or job.get("min_years", 0)
    if not required_skills or not job_title:
        raise HTTPException(status_code=400, detail="Butuh job_id atau (job_title + required_skills)")
    cache_key = make_key(
        "match",
        job_title,
        ",".join(sorted(required_skills)),
        ",".join(sorted(data.candidate_skills)),
        data.candidate_years_experience,
        min_years,
    )
    if cache_key in match_cache:
        return match_cache[cache_key]
    try:
        result = await match_score(
            data.candidate_skills,
            data.candidate_years_experience,
            job_title,
            required_skills,
            job_desc,
            min_years,
        )
        match_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI match gagal: {e}")


@api_router.post("/ai/salary-prediction", dependencies=[Depends(rate_limit(capacity=15, refill_per_sec=0.3))])
async def ai_salary_prediction(data: SalaryPredictionInput):
    cache_key = make_key(
        "salary",
        data.title.lower().strip(),
        data.location.lower().strip(),
        data.years_experience,
        (data.level or "mid").lower(),
        ",".join(sorted([s.lower() for s in data.skills])),
    )
    if cache_key in salary_cache:
        return salary_cache[cache_key]
    try:
        result = await predict_salary(
            title=data.title,
            location=data.location,
            years_experience=data.years_experience,
            level=data.level or "mid",
            skills=data.skills,
        )
        salary_cache[cache_key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI salary gagal: {e}")


# ---------- Seed (admin utility, idempotent) ----------
@api_router.post("/admin/seed")
async def admin_seed():
    result = await seed_database(db, include_demo_users=ENABLE_DEMO_USERS)
    categories_cache.clear()
    featured_jobs_cache.clear()
    return result


# Mount router
app.include_router(api_router)
app.include_router(build_admin_router(db), prefix="/api")

# ------ CORS ------
cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
if ENV == "production" and cors_origins_env.strip() == "*":
    logger.warning(
        "CORS_ORIGINS is '*' in production. Set explicit comma-separated origins for safety."
    )
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # Sanity warn for weak JWT secret in production
    if ENV == "production":
        secret = os.environ.get("JWT_SECRET", "")
        if not secret or "change-in-production" in secret or len(secret) < 32:
            logger.warning(
                "Weak/insecure JWT_SECRET detected in production. Rotate to a strong 32+ char random value."
            )
    # Create indexes (idempotent)
    await db.users.create_index("email", unique=True)
    await db.companies.create_index("slug", unique=True)
    await db.jobs.create_index("slug", unique=True)
    await db.jobs.create_index([("status", 1), ("created_at", -1)])
    await db.jobs.create_index([("title", "text"), ("description", "text"), ("skills", "text")])
    await db.applications.create_index([("job_id", 1), ("candidate_id", 1)], unique=True)
    await db.saved_jobs.create_index([("user_id", 1), ("job_id", 1)], unique=True)
    await db.categories.create_index("slug", unique=True)
    # Seed if empty
    if ENABLE_DEMO_SEED and await db.categories.count_documents({}) == 0:
        logger.info("Seeding initial demo data...")
        try:
            res = await seed_database(db, include_demo_users=ENABLE_DEMO_USERS)
            logger.info(f"Seed done: {res}")
        except Exception as e:
            logger.error(f"Seed failed: {e}")

    # Backfill missing embeddings (best effort, skip on failure)
    try:
        missing = await db.jobs.count_documents({"embedding": {"$in": [None, []]}})
        if missing == 0:
            missing = await db.jobs.count_documents({"embedding": {"$exists": False}})
        if missing > 0:
            logger.info("Backfilling embeddings for %d jobs...", missing)
            cursor = db.jobs.find(
                {"$or": [{"embedding": {"$exists": False}}, {"embedding": {"$in": [None, []]}}]},
                {"_id": 0},
            ).limit(500)
            jobs = await cursor.to_list(500)
            for j in jobs:
                try:
                    vec = embed_text(job_text(j))
                    await db.jobs.update_one({"id": j["id"]}, {"$set": {"embedding": vec}})
                except Exception as e:
                    logger.warning("Embedding backfill failed for %s: %s", j.get("id"), e)
            logger.info("Embedding backfill complete.")
    except Exception as e:
        logger.warning("Embedding backfill skipped: %s", e)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
