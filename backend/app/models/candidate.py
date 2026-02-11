"""Candidate-related models."""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, JSON, Float, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class Candidate(Base, TimeStampMixin):
    """Candidate profile model."""
    
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Basic Info
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    location = Column(String(255))
    timezone = Column(String(50))
    
    # Profile
    headline = Column(String(500))  # Current role/title
    summary = Column(Text)  # Bio/about
    avatar_url = Column(String(500))
    resume_url = Column(String(500))  # S3 URL
    portfolio_url = Column(String(500))
    
    # Social Links
    linkedin_url = Column(String(500), index=True)
    github_url = Column(String(500))
    twitter_url = Column(String(500))
    website_url = Column(String(500))
    
    # Parsed Resume Data
    total_experience_years = Column(Integer)  # Total years of experience
    parsed_resume = Column(JSON, default=dict)  # Full parsed data
    
    # AI Features
    resume_embedding = Column(Vector(1536))  # For semantic search
    ai_summary = Column(Text)  # AI-generated summary
    quality_score = Column(Float)  # AI quality score 0-100
    tags = Column(JSON, default=list)  # AI-generated tags
    
    # Job Search
    desired_salary_min = Column(Integer)
    desired_salary_max = Column(Integer)
    desired_locations = Column(JSON, default=list)
    open_to_remote = Column(Boolean, default=False)
    available_from = Column(String(255))
    notice_period_days = Column(Integer)
    
    # Privacy
    is_active = Column(Boolean, default=True)
    opted_in_marketing = Column(Boolean, default=False)
    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_date = Column(String(255))
    
    # Source tracking
    source_id = Column(UUID(as_uuid=False), ForeignKey("candidate_sources.id", ondelete="SET NULL"))
    source_details = Column(JSON, default=dict)  # Additional source info
    
    # Relationships
    organization = relationship("Organization", back_populates="candidates")
    source = relationship("CandidateSource", back_populates="candidates")
    experiences = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    education = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get candidate's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Candidate {self.full_name}>"


class CandidateExperience(Base, TimeStampMixin):
    """Candidate work experience."""
    
    __tablename__ = "candidate_experiences"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    candidate_id = Column(UUID(as_uuid=False), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(String(255))
    end_date = Column(String(255))  # Null if current
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="experiences")
    
    def __repr__(self):
        return f"<Experience {self.title} at {self.company}>"


class CandidateEducation(Base, TimeStampMixin):
    """Candidate education history."""
    
    __tablename__ = "candidate_education"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    candidate_id = Column(UUID(as_uuid=False), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(255))  # e.g., "Bachelor of Science"
    field_of_study = Column(String(255))  # e.g., "Computer Science"
    start_date = Column(String(255))
    end_date = Column(String(255))
    grade = Column(String(50))  # GPA or grade
    description = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="education")
    
    def __repr__(self):
        return f"<Education {self.degree} from {self.institution}>"


class CandidateSkill(Base, TimeStampMixin):
    """Candidate skills."""
    
    __tablename__ = "candidate_skills"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    candidate_id = Column(UUID(as_uuid=False), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100))  # e.g., "Programming Language", "Framework"
    proficiency_level = Column(Integer)  # 1-5 scale
    years_of_experience = Column(Integer)
    is_verified = Column(Boolean, default=False)  # Verified through assessment
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    
    def __repr__(self):
        return f"<Skill {self.name}>"


class CandidateSource(Base, TimeStampMixin):
    """Candidate source tracking."""
    
    __tablename__ = "candidate_sources"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)  # e.g., "LinkedIn", "Referral", "Job Board"
    type = Column(String(50))  # e.g., "job_board", "referral", "direct", "agency"
    cost_per_candidate = Column(Float)  # For tracking ROI
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    candidates = relationship("Candidate", back_populates="source")
    
    def __repr__(self):
        return f"<CandidateSource {self.name}>"
