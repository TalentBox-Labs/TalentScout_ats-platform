"""
Pydantic schemas for AI services.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ResumeParseRequest(BaseModel):
    """Schema for resume parsing request."""
    # File is handled via UploadFile in endpoint
    pass


class ResumeParseResponse(BaseModel):
    """Schema for resume parsing response."""
    success: bool
    data: Dict[str, Any]
    message: str


class CandidateMatchRequest(BaseModel):
    """Schema for candidate matching request."""
    job_id: UUID
    limit: Optional[int] = Field(20, ge=1, le=100)
    min_score: Optional[float] = Field(0.6, ge=0.0, le=1.0)


class CandidateMatchResult(BaseModel):
    """Schema for individual match result."""
    candidate_id: str
    first_name: str
    last_name: str
    email: str
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    location: Optional[str] = None
    years_of_experience: Optional[int] = None
    match_score: float
    explanation: str


class CandidateMatchResponse(BaseModel):
    """Schema for candidate matching response."""
    job_id: str
    total_matches: int
    matches: List[CandidateMatchResult]


class EmailGenerationRequest(BaseModel):
    """Schema for email generation request."""
    template_type: str = Field(..., pattern="^(interview_invitation|rejection|offer|follow_up|assessment|welcome|reminder)$")
    context: Dict[str, Any] = Field(..., description="Context data for email generation")
    tone: Optional[str] = Field("professional", pattern="^(professional|friendly|formal|casual)$")


class EmailGenerationResponse(BaseModel):
    """Schema for email generation response."""
    subject: str
    body: str
    template_type: str


class QuestionGenerationRequest(BaseModel):
    """Schema for question generation request."""
    job_id: Optional[UUID] = None
    job_context: Optional[Dict[str, Any]] = None
    question_types: Optional[List[str]] = Field(default=["technical", "behavioral"], description="Types of questions to generate")
    count: Optional[int] = Field(10, ge=1, le=50)


class InterviewQuestion(BaseModel):
    """Schema for individual interview question."""
    question: str
    type: str
    category: str
    difficulty: Optional[str] = None
    suggested_answer_points: Optional[List[str]] = None


class QuestionGenerationResponse(BaseModel):
    """Schema for question generation response."""
    questions: List[InterviewQuestion]
    total: int


class JobDescriptionRequest(BaseModel):
    """Schema for job description generation request."""
    title: str = Field(..., min_length=1)
    department: Optional[str] = None
    experience_level: str = Field(default="mid", pattern="^(entry|mid|senior|lead|executive)$")
    key_skills: List[str] = Field(..., min_items=1)
    additional_context: Optional[str] = None


class JobDescriptionResponse(BaseModel):
    """Schema for job description generation response."""
    title: str
    description: str
    requirements: str
    responsibilities: str
    suggested_skills: List[str]
