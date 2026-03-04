"""
Pydantic schemas for communication management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class EmailTemplateCreate(BaseModel):
    """Schema for creating an email template."""
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    template_type: str = Field(..., pattern="^(interview_invitation|rejection|offer|follow_up|assessment|welcome|reminder|custom)$")
    variables: Optional[List[str]] = None


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateResponse(BaseModel):
    """Schema for email template response."""
    id: UUID
    name: str
    subject: str
    body: str
    template_type: str
    variables: List[str]
    is_system_template: bool
    organization_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommunicationCreate(BaseModel):
    """Schema for sending communication."""
    candidate_id: UUID
    application_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    use_ai_enhancement: bool = False


class CommunicationResponse(BaseModel):
    """Schema for communication response."""
    id: UUID
    candidate_id: UUID
    application_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    subject: str
    body: str
    channel: str
    direction: str
    status: str
    sent_by_id: Optional[UUID] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailSequenceStepCreate(BaseModel):
    """Schema for creating an email sequence step."""
    template_id: UUID
    delay_days: int = Field(..., ge=0)
    order: int = Field(..., ge=1)


class EmailSequenceCreate(BaseModel):
    """Schema for creating an email sequence."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_event: str = Field(..., pattern="^(application_submitted|interview_scheduled|offer_extended|custom)$")
    steps: List[EmailSequenceStepCreate] = Field(..., min_items=1)


class EmailSequenceStepResponse(BaseModel):
    """Schema for email sequence step response."""
    id: UUID
    sequence_id: UUID
    template_id: UUID
    delay_days: int
    order: int
    
    class Config:
        from_attributes = True


class EmailSequenceResponse(BaseModel):
    """Schema for email sequence response."""
    id: UUID
    name: str
    description: Optional[str] = None
    trigger_event: str
    is_active: bool
    organization_id: UUID
    created_at: datetime
    steps: Optional[List[EmailSequenceStepResponse]] = None
    
    class Config:
        from_attributes = True


class EmailSequenceEnrollRequest(BaseModel):
    """Schema for enrolling candidate in sequence."""
    candidate_id: UUID
    application_id: Optional[UUID] = None
