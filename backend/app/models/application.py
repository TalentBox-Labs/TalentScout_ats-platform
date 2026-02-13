"""Application and pipeline models."""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class ApplicationStatus(str, enum.Enum):
    """Application status enum."""
    ACTIVE = "active"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ON_HOLD = "on_hold"


class ActivityType(str, enum.Enum):
    """Activity type enum."""
    CREATED = "created"
    STAGE_CHANGED = "stage_changed"
    NOTE_ADDED = "note_added"
    EMAIL_SENT = "email_sent"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ASSESSMENT_COMPLETED = "assessment_completed"
    SCREENING_COMPLETED = "screening_completed"
    STATUS_CHANGED = "status_changed"
    SCORE_UPDATED = "score_updated"


class Application(Base, TimeStampMixin):
    """Application model - links candidate to job."""
    
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    
    # Status & Stage
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.ACTIVE, index=True)
    current_stage = Column(String, ForeignKey("job_stages.id", ondelete="SET NULL"))
    
    # Application Data
    cover_letter = Column(Text)
    resume_url = Column(String(500))  # Can be different from candidate's main resume
    application_answers = Column(JSON, default=dict)  # Custom question answers
    
    # AI Scoring
    ai_match_score = Column(Float)  # 0-100 AI match score
    ai_insights = Column(JSON, default=dict)  # AI-generated insights
    ai_strengths = Column(JSON, default=list)  # AI-identified strengths
    ai_concerns = Column(JSON, default=list)  # AI-identified concerns
    ai_recommendation = Column(String(50))  # "strong_fit", "maybe", "not_fit"
    
    # Manual Scoring
    manual_score = Column(Float)  # Recruiter's manual score
    
    # Metadata
    applied_at = Column(String(255))
    source = Column(String(100))  # How they applied
    referrer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))  # If referred
    
    # Flags
    is_flagged = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    current_stage_obj = relationship("JobStage", back_populates="applications")
    referrer = relationship("User")
    activities = relationship("ApplicationActivity", back_populates="application", cascade="all, delete-orphan")
    notes = relationship("ApplicationNote", back_populates="application", cascade="all, delete-orphan")
    scores = relationship("ApplicationScore", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application {self.candidate_id} for {self.job_id}>"


class ApplicationActivity(Base, TimeStampMixin):
    """Activity log for applications."""
    
    __tablename__ = "application_activities"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    activity_metadata = Column(JSON, default=dict)  # Additional data
    
    # Relationships
    application = relationship("Application", back_populates="activities")
    user = relationship("User", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity {self.activity_type} for {self.application_id}>"


class ApplicationNote(Base, TimeStampMixin):
    """Notes/comments on applications."""
    
    __tablename__ = "application_notes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=False)  # Private to user only
    mentions = Column(JSON, default=list)  # List of mentioned user IDs
    attachments = Column(JSON, default=list)  # File attachments
    
    # Relationships
    application = relationship("Application", back_populates="notes")
    user = relationship("User", back_populates="comments")
    
    def __repr__(self):
        return f"<ApplicationNote by {self.user_id}>"


class ApplicationScore(Base, TimeStampMixin):
    """Scoring/evaluation for applications."""
    
    __tablename__ = "application_scores"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    category = Column(String(100), nullable=False)  # e.g., "Technical Skills", "Culture Fit"
    score = Column(Float, nullable=False)  # Score value
    max_score = Column(Float, default=10.0)  # Maximum possible score
    notes = Column(Text)
    
    # Relationships
    application = relationship("Application", back_populates="scores")
    
    def __repr__(self):
        return f"<ApplicationScore {self.category}: {self.score}/{self.max_score}>"
