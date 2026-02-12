"""
Pydantic schemas for interview management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class InterviewCreate(BaseModel):
    """Schema for scheduling an interview."""
    application_id: UUID
    scheduled_at: datetime
    duration_minutes: int = Field(60, ge=15, le=480)
    interview_type: str = Field(..., pattern="^(phone|video|onsite|technical|hr|final)$")
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    participant_ids: List[UUID] = Field(..., min_items=1)


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    interview_type: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|completed|cancelled|rescheduled|no_show)$")


class InterviewRescheduleRequest(BaseModel):
    """Schema for rescheduling an interview."""
    new_scheduled_at: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    reason: Optional[str] = None


class InterviewFeedbackCreate(BaseModel):
    """Schema for submitting interview feedback."""
    rating: int = Field(..., ge=1, le=5)
    feedback_text: str = Field(..., min_length=1)
    strengths: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    recommendation: str = Field(..., pattern="^(strong_yes |yes|maybe|no|strong_no)$")


class InterviewFeedbackResponse(BaseModel):
    """Schema for interview feedback response."""
    id: UUID
    interview_id: UUID
    user_id: UUID
    rating: int
    feedback_text: str
    strengths: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    recommendation: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    """Schema for interview list response (simplified)."""
    id: UUID
    application_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    interview_type: str
    status: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    
    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    """Schema for interview response with full details."""
    id: UUID
    application_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    interview_type: str
    status: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
