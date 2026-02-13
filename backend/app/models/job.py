"""Job-related models."""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Integer, Boolean, JSON, Float
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class JobStatus(str, enum.Enum):
    """Job status enum."""
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job type enum."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class ExperienceLevel(str, enum.Enum):
    """Experience level enum."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class Job(Base, TimeStampMixin):
    """Job posting model."""
    
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    # Job Details
    department = Column(String(100))
    location = Column(String(255))
    is_remote = Column(Boolean, default=False)
    job_type = Column(SQLEnum(JobType), nullable=False, default=JobType.FULL_TIME)
    experience_level = Column(SQLEnum(ExperienceLevel), default=ExperienceLevel.MID)
    
    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(3), default="USD")
    
    # Status
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.DRAFT, index=True)
    openings = Column(Integer, default=1)  # Number of positions
    
    # AI Features
    embedding = Column(JSON, default=list)  # OpenAI embedding dimension (using JSON for SQLite dev)
    skills_required = Column(JSON, default=list)  # List of required skills
    skills_preferred = Column(JSON, default=list)  # List of preferred skills
    
    # Settings
    is_internal = Column(Boolean, default=False)  # Internal posting only
    application_deadline = Column(String(255))
    settings = Column(JSON, default=dict)  # Custom settings
    
    # Relationships
    organization = relationship("Organization", back_populates="jobs")
    created_by_user = relationship("User", back_populates="created_jobs", foreign_keys=[created_by])
    stages = relationship("JobStage", back_populates="job", cascade="all, delete-orphan", order_by="JobStage.order")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job {self.title}>"


class JobStage(Base, TimeStampMixin):
    """Pipeline stages for a job."""
    
    __tablename__ = "job_stages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)  # Stage order in pipeline
    color = Column(String(7), default="#3B82F6")  # Hex color for UI
    
    # Stage settings
    is_system = Column(Boolean, default=False)  # System stages can't be deleted
    auto_reject_days = Column(Integer)  # Auto-reject after X days
    settings = Column(JSON, default=dict)
    
    # Relationships
    job = relationship("Job", back_populates="stages")
    applications = relationship("Application", back_populates="current_stage_obj")
    
    def __repr__(self):
        return f"<JobStage {self.name} for Job {self.job_id}>"


class JobTemplate(Base, TimeStampMixin):
    """Reusable job templates."""
    
    __tablename__ = "job_templates"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    job_type = Column(SQLEnum(JobType))
    experience_level = Column(SQLEnum(ExperienceLevel))
    department = Column(String(100))
    
    skills_required = Column(JSON, default=list)
    skills_preferred = Column(JSON, default=list)
    default_stages = Column(JSON, default=list)  # Default pipeline stages
    
    is_public = Column(Boolean, default=False)  # Shared across organization
    
    def __repr__(self):
        return f"<JobTemplate {self.name}>"
