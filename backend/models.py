"""Pydantic models for Talentiv Jobs."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict, EmailStr


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


# ---------- Enums ----------
Role = Literal["candidate", "employer", "admin"]
EmploymentType = Literal["full_time", "part_time", "contract", "internship", "freelance"]
WorkMode = Literal["onsite", "remote", "hybrid"]
ExperienceLevel = Literal["entry", "junior", "mid", "senior", "lead"]
JobStatus = Literal["draft", "published", "paused", "closed"]
ApplicationStatus = Literal["applied", "reviewing", "interview", "rejected", "hired"]


# ---------- User & Auth ----------
class UserPublic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: EmailStr
    name: str
    role: Role
    created_at: str


class UserInDB(UserPublic):
    password_hash: str
    company_id: Optional[str] = None  # for employers
    is_disabled: bool = False


class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    role: Role = "candidate"
    company_name: Optional[str] = None  # required if role=employer


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserPublic


# ---------- Profile ----------
class Experience(BaseModel):
    title: str
    company: str
    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    degree: str
    institution: str
    start: Optional[str] = None
    end: Optional[str] = None
    gpa: Optional[str] = None


class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    resume_text: Optional[str] = None  # cached parsed text
    updated_at: str = Field(default_factory=now_iso)


class ProfileUpdateInput(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None


# ---------- Category ----------
class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=new_id)
    name: str
    slug: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    order_rank: int = 0
    job_count: int = 0


# ---------- Company ----------
class Company(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=new_id)
    owner_id: Optional[str] = None
    name: str
    slug: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


class CompanyInput(BaseModel):
    name: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None


# ---------- Job ----------
class Job(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=new_id)
    company_id: str
    title: str
    slug: str
    description: str
    requirements: str
    skills: List[str] = Field(default_factory=list)
    employment_type: EmploymentType = "full_time"
    work_mode: WorkMode = "onsite"
    experience_level: ExperienceLevel = "mid"
    min_years: int = 0
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "IDR"
    location: str
    category_id: Optional[str] = None
    status: JobStatus = "published"
    created_at: str = Field(default_factory=now_iso)
    views: int = 0
    applications_count: int = 0
    is_featured: bool = False
    moderation_reason: Optional[str] = None
    embedding: Optional[List[float]] = None


class JobInput(BaseModel):
    title: str
    description: str
    requirements: str
    skills: List[str] = Field(default_factory=list)
    employment_type: EmploymentType = "full_time"
    work_mode: WorkMode = "onsite"
    experience_level: ExperienceLevel = "mid"
    min_years: int = 0
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: str
    category_id: Optional[str] = None
    status: JobStatus = "published"


class JobListItem(BaseModel):
    id: str
    title: str
    slug: str
    company: dict  # {id,name,logo_url,location}
    location: str
    work_mode: WorkMode
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "IDR"
    skills: List[str] = []
    created_at: str
    category_id: Optional[str] = None
    match_score: Optional[int] = None


# ---------- Application ----------
class Application(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=new_id)
    job_id: str
    candidate_id: str
    cover_letter: Optional[str] = None
    status: ApplicationStatus = "applied"
    match_score: Optional[int] = None
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    rationale: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


class ApplicationInput(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


# ---------- Saved Job ----------
class SavedJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=new_id)
    user_id: str
    job_id: str
    created_at: str = Field(default_factory=now_iso)


# ---------- AI Input/Output ----------
class ResumeParseInput(BaseModel):
    text: Optional[str] = None
    pdf_base64: Optional[str] = None


class MatchScoreInput(BaseModel):
    candidate_skills: List[str]
    candidate_years_experience: int = 0
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    job_required_skills: Optional[List[str]] = None
    job_description: Optional[str] = None
    job_min_years: Optional[int] = 0


class MatchScoreOutput(BaseModel):
    score: int
    rationale: str
    matched_skills: List[str]
    missing_skills: List[str]
    recommendation: str


class SalaryPredictionInput(BaseModel):
    title: str
    location: str
    years_experience: int = 0
    level: Optional[str] = "mid"
    skills: List[str] = Field(default_factory=list)


class SalaryPredictionOutput(BaseModel):
    salary_min: int
    salary_max: int
    currency: str = "IDR"
    period: str = "month"
    rationale: str
    confidence: str
    assumptions: List[str] = Field(default_factory=list)
