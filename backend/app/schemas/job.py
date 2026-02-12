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

