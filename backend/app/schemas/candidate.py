"""Candidate-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, Field

from app.models.application import ApplicationStatus


class CandidateBase(BaseModel):
    """Base schema for candidate data."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    total_experience_years: Optional[int] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    desired_locations: List[str] = Field(default_factory=list)
    open_to_remote: bool = False
    tags: List[str] = Field(default_factory=list)
    source_details: Dict = Field(default_factory=dict)


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate."""

    source_id: Optional[str] = None


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    total_experience_years: Optional[int] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    desired_locations: Optional[List[str]] = None
    open_to_remote: Optional[bool] = None
    tags: Optional[List[str]] = None
    source_id: Optional[str] = None
    source_details: Optional[Dict] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate responses."""

    id: str
    organization_id: str
    is_active: bool
    gdpr_consent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateApplicationSummary(BaseModel):
    """Lightweight view of applications for a candidate."""

    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    current_stage: Optional[str] = None
    applied_at: Optional[str] = None

    class Config:
        from_attributes = True


class CandidateSearchRequest(BaseModel):
    """Search and filter payload for candidates search."""

    search: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    open_to_remote: Optional[bool] = None
    min_experience_years: Optional[int] = None
    limit: int = 50
    offset: int = 0


class CandidateImportItem(CandidateBase):
    """Single candidate item for bulk import."""

    source_id: Optional[str] = None


class CandidateImportResponse(BaseModel):
    """Response after bulk import of candidates."""

    created: int
    skipped: int


class ResumeUploadResponse(BaseModel):
    """Response payload for resume upload."""

    message: str
    candidate: CandidateResponse
    parsed_contact: Dict

