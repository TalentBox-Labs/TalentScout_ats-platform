"""Assessment and screening models."""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Float, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class QuestionType(str, enum.Enum):
    """Question type enum."""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    RATING = "rating"
    FILE_UPLOAD = "file_upload"
    VIDEO = "video"
    CODE = "code"


class AssessmentStatus(str, enum.Enum):
    """Assessment status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class ScreeningTemplate(Base, TimeStampMixin):
    """Template for screening questions."""
    
    __tablename__ = "screening_templates"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    questions = Column(JSON, nullable=False)  # List of questions with structure
    
    # Settings
    time_limit_minutes = Column(Integer)  # Total time limit
    passing_score = Column(Float)  # Minimum score to pass
    is_public = Column(Boolean, default=False)  # Shared across organization
    
    # AI Features
    is_ai_generated = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<ScreeningTemplate {self.name}>"


class Assessment(Base, TimeStampMixin):
    """Assessment instance for a candidate."""
    
    __tablename__ = "assessments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(String, ForeignKey("screening_templates.id", ondelete="SET NULL"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.PENDING, index=True)
    
    # Timing
    sent_at = Column(String(255))
    started_at = Column(String(255))
    completed_at = Column(String(255))
    expires_at = Column(String(255))
    time_taken_minutes = Column(Integer)
    
    # Access
    access_token = Column(String(255), unique=True, index=True)  # Unique token for candidate access
    
    # Relationships
    application = relationship("Application", back_populates="assessments")
    template = relationship("ScreeningTemplate")
    responses = relationship("AssessmentResponse", back_populates="assessment", cascade="all, delete-orphan")
    scores = relationship("AssessmentScore", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment {self.title} for {self.application_id}>"


class AssessmentResponse(Base, TimeStampMixin):
    """Candidate responses to assessment questions."""
    
    __tablename__ = "assessment_responses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    
    question_id = Column(String(100), nullable=False)  # Reference to question in template
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    
    # Response
    response_text = Column(Text)
    response_data = Column(JSON)  # For complex responses (choices, ratings, etc.)
    file_urls = Column(JSON, default=list)  # For file upload questions
    
    # Scoring
    is_correct = Column(Boolean)  # For questions with right/wrong answers
    points_earned = Column(Float)
    max_points = Column(Float)
    
    # AI Evaluation
    ai_evaluation = Column(Text)  # AI assessment of the response
    ai_score = Column(Float)  # AI-generated score
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    
    def __repr__(self):
        return f"<AssessmentResponse {self.question_id}>"


class AssessmentScore(Base, TimeStampMixin):
    """Overall scoring for assessments."""
    
    __tablename__ = "assessment_scores"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    scored_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Scores
    total_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage_score = Column(Float)  # (total_score / max_score) * 100
    
    # Evaluation
    passed = Column(Boolean)
    feedback = Column(Text)
    recommendation = Column(String(50))  # "proceed", "reject", "review"
    
    # AI Features
    is_ai_scored = Column(Boolean, default=False)
    ai_insights = Column(JSON, default=dict)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="scores")
    
    def __repr__(self):
        return f"<AssessmentScore {self.total_score}/{self.max_score}>"
