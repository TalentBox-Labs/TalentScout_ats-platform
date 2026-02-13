"""Interview-related models."""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class InterviewType(str, enum.Enum):
    """Interview type enum."""
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"


class InterviewStatus(str, enum.Enum):
    """Interview status enum."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class Interview(Base, TimeStampMixin):
    """Interview model."""
    
    __tablename__ = "interviews"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    
    # Interview Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    interview_type = Column(SQLEnum(InterviewType), nullable=False, default=InterviewType.VIDEO)
    status = Column(SQLEnum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED, index=True)
    
    # Scheduling
    scheduled_at = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="UTC")
    
    # Location/Link
    location = Column(String(500))  # Physical address or "Remote"
    meeting_link = Column(String(500))  # Zoom/Meet/Teams link
    meeting_id = Column(String(255))
    meeting_password = Column(String(255))
    
    # Metadata
    instructions = Column(Text)  # Instructions for candidate
    calendar_event_id = Column(String(255))  # Google/Outlook event ID
    reminder_sent = Column(Boolean, default=False)
    
    # AI Features
    ai_questions = Column(JSON, default=list)  # AI-generated interview questions
    ai_summary = Column(Text)  # AI-generated summary after interview
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    participants = relationship("InterviewParticipant", back_populates="interview", cascade="all, delete-orphan")
    feedback = relationship("InterviewFeedback", back_populates="interview", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interview {self.title} at {self.scheduled_at}>"


class InterviewParticipant(Base, TimeStampMixin):
    """Interview participants (interviewers)."""
    
    __tablename__ = "interview_participants"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    is_required = Column(Boolean, default=True)  # Required vs optional attendee
    has_confirmed = Column(Boolean, default=False)
    response_status = Column(String(20))  # "accepted", "declined", "tentative"
    
    # Relationships
    interview = relationship("Interview", back_populates="participants")
    user = relationship("User", back_populates="interviews")
    
    def __repr__(self):
        return f"<InterviewParticipant {self.user_id} in {self.interview_id}>"


class InterviewFeedback(Base, TimeStampMixin):
    """Feedback from interviewers."""
    
    __tablename__ = "interview_feedback"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    interviewer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Feedback
    overall_rating = Column(Integer)  # 1-5 scale
    technical_rating = Column(Integer)
    communication_rating = Column(Integer)
    culture_fit_rating = Column(Integer)
    
    strengths = Column(Text)
    concerns = Column(Text)
    notes = Column(Text)
    recommendation = Column(String(50))  # "strong_hire", "hire", "no_hire", "strong_no_hire"
    
    # Structured feedback
    questions_answers = Column(JSON, default=list)  # Q&A pairs
    custom_ratings = Column(JSON, default=dict)  # Custom rating categories
    
    is_submitted = Column(Boolean, default=False)
    submitted_at = Column(String(255))
    
    # Relationships
    interview = relationship("Interview", back_populates="feedback")
    
    def __repr__(self):
        return f"<InterviewFeedback for {self.interview_id}>"
