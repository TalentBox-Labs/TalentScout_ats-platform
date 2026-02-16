"""
Pydantic schemas for job management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class JobCreate(BaseModel):
    """Schema for creating a job."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = Field(default="full_time", pattern="^(full_time|part_time|contract|internship|temporary)$")
    experience_level: Optional[str] = Field(default="mid", pattern="^(entry|junior|mid|senior|lead|principal)$")
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    skills_required: Optional[List[str]] = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    skills_required: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(draft|open|closed|on_hold)$")


class JobStageCreate(BaseModel):
    """Schema for creating a job stage."""
    name: str = Field(..., min_length=1, max_length=100)
    order: int = Field(..., ge=1)


class JobStageUpdate(BaseModel):
    """Schema for updating a job stage."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    order: Optional[int] = Field(None, ge=1)


class JobStageResponse(BaseModel):
    """Schema for job stage response."""
    id: UUID
    job_id: UUID
    name: str
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    """Schema for job response."""
    id: UUID
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: str
    experience_level: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    skills_required: List[str]
    status: str
    organization_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    stages: Optional[List[JobStageResponse]] = None
    is_public: bool
    public_slug: Optional[str] = None
    share_count: int
    share_metadata: Dict[str, Any]
    og_image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    view_count: int
    show_salary_public: bool
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for job list response with application count."""
    id: UUID
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: str
    experience_level: str
    status: str
    created_at: datetime
    applications_count: int = 0
    
    class Config:
        from_attributes = True


class JobTemplateCreate(BaseModel):
    """Schema for creating a job template."""
    name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    job_type: str = Field(default="full_time")
    experience_level: str = Field(default="mid")
    skills_required: Optional[List[str]] = None


class JobTemplateResponse(BaseModel):
    """Schema for job template response."""
    id: UUID
    name: str
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    job_type: str
    experience_level: str
    skills_required: List[str]
    is_public: bool
    organization_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublicJobResponse(BaseModel):
    """Schema for public job response (no sensitive data)."""
    id: UUID
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: str
    experience_level: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    skills_required: List[str]
    organization_name: Optional[str] = None
    created_at: datetime
    published_at: Optional[datetime] = None
    view_count: int
    share_count: int
    
    class Config:
        from_attributes = True


class ShareLinkResponse(BaseModel):
    """Schema for share link response."""
    platform: str
    url: str
    text: str


class ShareLinksResponse(BaseModel):
    """Schema for aggregate share links response."""
    job_id: UUID
    job_title: str
    public_url: str
    share_links: List[ShareLinkResponse]


class TrackShareRequest(BaseModel):
    """Schema for tracking share requests."""
    platform: str = Field(..., pattern="^(linkedin|twitter|facebook|email|copy)$")


class SalaryVisibilityUpdate(BaseModel):
    """Schema for updating salary visibility."""
    show_salary_public: bool