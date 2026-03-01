"""
Pydantic schemas for assessments.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ScreeningQuestionCreate(BaseModel):
    """Schema for creating a screening question."""
    question_text: str = Field(..., min_length=1)
    question_type: str = Field(..., pattern="^(multiple_choice|text|code|video)$")
    required: bool = True
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = Field(10, ge=0)


class ScreeningQuestionResponse(BaseModel):
    """Schema for screening question response."""
    id: UUID
    template_id: UUID
    question_text: str
    question_type: str
    required: bool
    options: Optional[List[str]] = None
    points: Optional[int] = None
    
    class Config:
        from_attributes = True


class ScreeningTemplateCreate(BaseModel):
    """Schema for creating a screening template."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str = Field(default="screening", pattern="^(screening|technical|skills|culture_fit)$")
    questions: List[ScreeningQuestionCreate] = Field(..., min_items=1)


class ScreeningTemplateUpdate(BaseModel):
    """Schema for updating a screening template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ScreeningTemplateResponse(BaseModel):
    """Schema for screening template response."""
    id: UUID
    name: str
    description: Optional[str] = None
    type: str
    is_active: bool
    organization_id: UUID
    created_at: datetime
    questions: Optional[List[ScreeningQuestionResponse]] = None
    
    class Config:
        from_attributes = True


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment."""
    application_id: UUID
    template_id: UUID


class AssessmentResponseCreate(BaseModel):
    """Schema for submitting an assessment response."""
    question_id: UUID
    response_text: str


class AssessmentResponseResponse(BaseModel):
    """Schema for assessment response."""
    id: UUID
    assessment_id: UUID
    question_id: UUID
    response_text: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    """Schema for assessment."""
    id: UUID
    application_id: UUID
    template_id: UUID
    status: str
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    template: Optional[ScreeningTemplateResponse] = None
    responses: Optional[List[AssessmentResponseResponse]] = None
    
    class Config:
        from_attributes = True
