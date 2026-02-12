<<<<<<< HEAD
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
    employment_type: Optional[str] = Field(default="full_time", pattern="^(full_time|part_time|contract|temporary|internship)$")
    experience_level: Optional[str] = Field(default="mid", pattern="^(entry|mid|senior|lead|executive)$")
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
    employment_type: Optional[str] = None
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
    stage_type: str = Field(default="custom", pattern="^(application|screening|interview|assessment|offer|hired|rejected|custom)$")


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
    stage_type: str
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
    employment_type: str
    experience_level: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    skills_required: List[str]
    status: str
    organization_id: UUID
    created_by_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    stages: Optional[List[JobStageResponse]] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for job list response with application count."""
    id: UUID
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: str
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
    employment_type: str = Field(default="full_time")
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
    employment_type: str
    experience_level: str
    skills_required: List[str]
    is_public: bool
    organization_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
=======
"""Job-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.job import JobStatus, JobType, ExperienceLevel
from app.models.application import ApplicationStatus


class JobBase(BaseModel):
  """Base schema for job data."""

  title: str = Field(..., min_length=1, max_length=255)
  description: str
  requirements: Optional[str] = None
  responsibilities: Optional[str] = None
  benefits: Optional[str] = None
  department: Optional[str] = None
  location: Optional[str] = None
  is_remote: bool = False
  job_type: JobType = JobType.FULL_TIME
  experience_level: ExperienceLevel = ExperienceLevel.MID
  salary_min: Optional[int] = None
  salary_max: Optional[int] = None
  salary_currency: str = "USD"
  openings: int = 1
  is_internal: bool = False
  application_deadline: Optional[str] = None
  skills_required: List[str] = Field(default_factory=list)
  skills_preferred: List[str] = Field(default_factory=list)
  settings: dict = Field(default_factory=dict)


class JobCreate(JobBase):
  """Schema for creating a job."""

  pass


class JobUpdate(BaseModel):
  """Schema for updating a job."""

  title: Optional[str] = Field(None, min_length=1, max_length=255)
  description: Optional[str] = None
  requirements: Optional[str] = None
  responsibilities: Optional[str] = None
  benefits: Optional[str] = None
  department: Optional[str] = None
  location: Optional[str] = None
  is_remote: Optional[bool] = None
  job_type: Optional[JobType] = None
  experience_level: Optional[ExperienceLevel] = None
  salary_min: Optional[int] = None
  salary_max: Optional[int] = None
  salary_currency: Optional[str] = None
  openings: Optional[int] = None
  status: Optional[JobStatus] = None
  is_internal: Optional[bool] = None
  application_deadline: Optional[str] = None
  skills_required: Optional[List[str]] = None
  skills_preferred: Optional[List[str]] = None
  settings: Optional[dict] = None


class JobResponse(JobBase):
  """Schema for job responses."""

  id: str
  organization_id: str
  created_by: Optional[str] = None
  status: JobStatus
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True


class JobStageBase(BaseModel):
  """Base schema for job stages."""

  name: str = Field(..., min_length=1, max_length=100)
  description: Optional[str] = None
  order: Optional[int] = None
  color: Optional[str] = "#3B82F6"
  is_system: bool = False
  auto_reject_days: Optional[int] = None
  settings: dict = Field(default_factory=dict)


class JobStageCreate(JobStageBase):
  """Schema for creating a job stage."""

  pass


class JobStageResponse(JobStageBase):
  """Schema for job stage responses."""

  id: str
  job_id: str
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True


class JobApplicationSummary(BaseModel):
  """Lightweight view of applications for a job."""

  id: str
  job_id: str
  candidate_id: str
  status: ApplicationStatus
  current_stage: Optional[str] = None
  applied_at: Optional[str] = None

  class Config:
    from_attributes = True

>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
