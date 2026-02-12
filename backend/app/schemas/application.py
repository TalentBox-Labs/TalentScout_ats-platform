"""
Pydantic schemas for application management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ApplicationCreate(BaseModel):
    """Schema for creating an application."""
    candidate_id: UUID
    job_id: UUID
    source: Optional[str] = "manual"
    cover_letter: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Schema for updating an application."""
    cover_letter: Optional[str] = None


class ApplicationStageUpdate(BaseModel):
    """Schema for moving application to different stage."""
    stage_id: UUID


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status."""
    status: str = Field(..., pattern="^(active|hired|rejected|withdrawn|on_hold)$")
    reason: Optional[str] = None


class NoteCreate(BaseModel):
    """Schema for creating a note."""
    content: str = Field(..., min_length=1)
    is_private: bool = False


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: UUID
    application_id: UUID
    user_id: UUID
    content: str
    is_private: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreCreate(BaseModel):
    """Schema for creating a score."""
    category: str = Field(..., min_length=1, max_length=100)
    score: float = Field(..., ge=0)
    max_score: float = Field(default=10.0, ge=1)
    comments: Optional[str] = None


class ScoreResponse(BaseModel):
    """Schema for score response."""
    id: UUID
    application_id: UUID
    user_id: UUID
    category: str
    score: float
    max_score: float
    comments: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    """Schema for activity response."""
    id: UUID
    application_id: UUID
    type: str
    description: str
    user_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    """Schema for application list response (simplified)."""
    id: UUID
    candidate_id: UUID
    job_id: UUID
    stage_id: Optional[UUID] = None
    status: str
    ai_match_score: Optional[float] = None
    created_at: datetime
    candidate: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    current_stage: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Schema for application response with full details."""
    id: UUID
    candidate_id: UUID
    job_id: UUID
    stage_id: Optional[UUID] = None
    status: str
    source: str
    cover_letter: Optional[str] = None
    ai_match_score: Optional[float] = None
    ai_insights: Optional[str] = None
    ai_strengths: Optional[List[str]] = None
    ai_concerns: Optional[List[str]] = None
    organization_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    candidate: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    current_stage: Optional[Dict[str, Any]] = None
    activities: Optional[List[ActivityResponse]] = None
    notes: Optional[List[NoteResponse]] = None
    scores: Optional[List[ScoreResponse]] = None
    
    class Config:
        from_attributes = True
