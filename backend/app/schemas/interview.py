"""
Pydantic schemas for interview management.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class InterviewCreate(BaseModel):
    """Schema for scheduling an interview."""
    application_id: UUID
    title: str
    scheduled_at: datetime
    duration_minutes: int = Field(60, ge=15, le=480)
    interview_type: str = Field(..., pattern="^(phone|video|onsite|technical|behavioral|panel)$")
    participant_ids: List[UUID] = Field(..., min_length=1)
    description: Optional[str] = None
    timezone: str = "UTC"
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    interview_type: Optional[str] = Field(None, pattern="^(phone|video|onsite|technical|behavioral|panel)$")
    description: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    instructions: Optional[str] = None
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
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    technical_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    culture_fit_rating: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    notes: Optional[str] = None
    recommendation: Optional[str] = Field(None, pattern="^(strong_hire|hire|no_hire|strong_no_hire)$")
    questions_answers: Optional[List[Dict[str, Any]]] = []
    custom_ratings: Optional[Dict[str, Any]] = {}
    is_submitted: bool = False


class InterviewFeedbackResponse(BaseModel):
    """Schema for interview feedback response."""
    id: UUID
    interview_id: UUID
    interviewer_id: Optional[UUID] = None
    overall_rating: Optional[int] = None
    technical_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    culture_fit_rating: Optional[int] = None
    strengths: Optional[str] = None
    concerns: Optional[str] = None
    notes: Optional[str] = None
    recommendation: Optional[str] = None
    questions_answers: Optional[List[Dict[str, Any]]] = None
    custom_ratings: Optional[Dict[str, Any]] = None
    is_submitted: bool
    submitted_at: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    """Schema for interview list response (simplified)."""
    id: UUID
    title: str
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
    title: str
    application_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    interview_type: str
    status: str
    description: Optional[str] = None
    timezone: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    instructions: Optional[str] = None
    ai_questions: List[Dict[str, Any]]
    ai_summary: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InterviewParticipantResponse(BaseModel):
    """Schema for interview participant response."""
    id: UUID
    interview_id: UUID
    user_id: UUID
    is_required: bool
    has_confirmed: bool
    response_status: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
