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
    total_experience_years: Optional[int] = None
    source: Optional[str] = "manual"


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""
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
    total_experience_years: Optional[int] = None


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
    total_experience_years: Optional[int] = None
    summary: Optional[str] = None
    source: str
    organization_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    experiences: Optional[List[ExperienceResponse]] = None
    education: Optional[List[EducationResponse]] = None
    skills: Optional[List[SkillResponse]] = None
    
    class Config:
        from_attributes = True
    

class CandidateListResponse(BaseModel):
    """Schema for candidate list response (simplified)."""
    id: UUID
    first_name: str
    last_name: str
    email: str
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    location: Optional[str] = None
    total_experience_years: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
    

class CandidateSearchRequest(BaseModel):
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