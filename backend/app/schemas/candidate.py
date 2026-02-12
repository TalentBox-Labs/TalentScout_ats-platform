<<<<<<< HEAD
"""
Pydantic schemas for candidate management.
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    years_of_experience: Optional[int] = None
    source: Optional[str] = "manual"
=======
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
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""
<<<<<<< HEAD
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    years_of_experience: Optional[int] = None


class ExperienceResponse(BaseModel):
    """Schema for experience response."""
    id: UUID
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class EducationResponse(BaseModel):
    """Schema for education response."""
    id: UUID
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    """Schema for skill response."""
    id: UUID
    name: str
    proficiency_level: Optional[str] = None
    
    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    """Schema for candidate response with full details."""
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    years_of_experience: Optional[int] = None
    summary: Optional[str] = None
    source: str
    organization_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    experiences: Optional[List[ExperienceResponse]] = None
    education: Optional[List[EducationResponse]] = None
    skills: Optional[List[SkillResponse]] = None
    
=======

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

>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    class Config:
        from_attributes = True


<<<<<<< HEAD
class CandidateListResponse(BaseModel):
    """Schema for candidate list response (simplified)."""
    id: UUID
    first_name: str
    last_name: str
    email: str
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    location: Optional[str] = None
    years_of_experience: Optional[int] = None
    created_at: datetime
    
=======
class CandidateApplicationSummary(BaseModel):
    """Lightweight view of applications for a candidate."""

    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    current_stage: Optional[str] = None
    applied_at: Optional[str] = None

>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    class Config:
        from_attributes = True


class CandidateSearchRequest(BaseModel):
<<<<<<< HEAD
    """Schema for semantic search request."""
    query: str = Field(..., min_length=1, description="Search query for semantic matching")
    limit: Optional[int] = Field(20, ge=1, le=100)
    min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")


class CandidateSearchResult(BaseModel):
    """Schema for individual search result."""
    candidate_id: str
    first_name: str
    last_name: str
    email: str
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    location: Optional[str] = None
    similarity_score: float
    match_explanation: str


class CandidateSearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    total_results: int
    results: List[CandidateSearchResult]
=======
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

>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
