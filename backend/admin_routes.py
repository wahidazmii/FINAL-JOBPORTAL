"""Admin-only endpoints for moderation."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import require_role


class AdminJobUpdate(BaseModel):
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    moderation_reason: Optional[str] = None


class AdminUserUpdate(BaseModel):
    is_disabled: Optional[bool] = None
    role: Optional[str] = None


class AdminCompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


def clean(doc):
    if doc is None:
        return None
    doc.pop("_id", None)
    return doc


def build_admin_router(db) -> APIRouter:
    router = APIRouter(prefix="/admin", dependencies=[Depends(require_role("admin"))])

    @router.get("/overview")
    async def overview():
        total_users = await db.users.count_documents({})
        total_candidates = await db.users.count_documents({"role": "candidate"})
        total_employers = await db.users.count_documents({"role": "employer"})
        total_admins = await db.users.count_documents({"role": "admin"})
        disabled_users = await db.users.count_documents({"is_disabled": True})
        total_companies = await db.companies.count_documents({})
        total_jobs = await db.jobs.count_documents({})
        active_jobs = await db.jobs.count_documents({"status": "published"})
        paused_jobs = await db.jobs.count_documents({"status": "paused"})
        closed_jobs = await db.jobs.count_documents({"status": "closed"})
        featured_jobs = await db.jobs.count_documents({"is_featured": True})
        total_apps = await db.applications.count_documents({})
        return {
            "users": {
                "total": total_users,
                "candidates": total_candidates,
                "employers": total_employers,
                "admins": total_admins,
                "disabled": disabled_users,
            },
            "companies": {"total": total_companies},
            "jobs": {
                "total": total_jobs,
                "published": active_jobs,
                "paused": paused_jobs,
                "closed": closed_jobs,
                "featured": featured_jobs,
            },
            "applications": {"total": total_apps},
        }

    # -------- Jobs --------
    @router.get("/jobs")
    async def list_jobs(q: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
        filters: dict = {}
        if q:
            filters["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]
        if status:
            filters["status"] = status
        cursor = db.jobs.find(filters, {"_id": 0}).sort("created_at", -1).limit(limit)
        jobs = await cursor.to_list(limit)
        # Enrich with company name
        result = []
        for j in jobs:
            co = await db.companies.find_one({"id": j["company_id"]}, {"_id": 0, "id": 1, "name": 1, "slug": 1})
            j["company"] = co or {}
            result.append(j)
        return result

    @router.put("/jobs/{job_id}")
    async def update_job(job_id: str, data: AdminJobUpdate):
        # Use exclude_unset + keep booleans (False is valid) - use model_dump(exclude_none=False)
        raw = data.model_dump(exclude_unset=True)
        update = {k: v for k, v in raw.items() if v is not None or isinstance(v, bool)}
        if not update:
            raise HTTPException(status_code=400, detail="No fields to update")
        res = await db.jobs.update_one({"id": job_id}, {"$set": update})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
        return clean(await db.jobs.find_one({"id": job_id}))

    @router.delete("/jobs/{job_id}")
    async def delete_job(job_id: str):
        res = await db.jobs.delete_one({"id": job_id})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lowongan tidak ditemukan")
        return {"ok": True}

    # -------- Users --------
    @router.get("/users")
    async def list_users(role: Optional[str] = None, q: Optional[str] = None, limit: int = 100):
        filters: dict = {}
        if role:
            filters["role"] = role
        if q:
            filters["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}},
            ]
        cursor = db.users.find(filters, {"_id": 0, "password_hash": 0}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(limit)

    @router.put("/users/{user_id}")
    async def update_user(user_id: str, data: AdminUserUpdate):
        raw = data.model_dump(exclude_unset=True)
        update = {k: v for k, v in raw.items() if v is not None or isinstance(v, bool)}
        if not update:
            raise HTTPException(status_code=400, detail="No fields to update")
        if "role" in update and update["role"] not in ("candidate", "employer", "admin"):
            raise HTTPException(status_code=400, detail="Invalid role")
        res = await db.users.update_one({"id": user_id}, {"$set": update})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")
        doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return doc

    # -------- Companies --------
    @router.get("/companies")
    async def list_companies(q: Optional[str] = None, limit: int = 100):
        filters: dict = {}
        if q:
            filters["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"industry": {"$regex": q, "$options": "i"}},
            ]
        cursor = db.companies.find(filters, {"_id": 0}).sort("created_at", -1).limit(limit)
        companies = await cursor.to_list(limit)
        for c in companies:
            c["job_count"] = await db.jobs.count_documents({"company_id": c["id"]})
        return companies

    @router.put("/companies/{company_id}")
    async def update_company(company_id: str, data: AdminCompanyUpdate):
        update = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
        if not update:
            raise HTTPException(status_code=400, detail="No fields")
        res = await db.companies.update_one({"id": company_id}, {"$set": update})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Company tidak ditemukan")
        return clean(await db.companies.find_one({"id": company_id}))

    return router
