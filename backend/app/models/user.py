"""User and Organization models."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    HIRING_MANAGER = "hiring_manager"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    VIEWER = "viewer"


class Organization(Base, TimeStampMixin):
    """Organization/Company model - multi-tenant support."""
    
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, index=True)
    logo_url = Column(String(500))
    website = Column(String(500))
    industry = Column(String(100))
    size = Column(String(50))  # e.g., "1-10", "11-50", "51-200"
    settings = Column(JSON, default=dict)  # Organization-wide settings
    is_active = Column(Boolean, default=True)
    
    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="organization", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization {self.name}>"


class User(Base, TimeStampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    avatar_url = Column(String(500))
    title = Column(String(100))  # Job title
    bio = Column(Text)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(String(255))
    
    # OAuth fields
    google_id = Column(String(255), unique=True, index=True)
    microsoft_id = Column(String(255), unique=True, index=True)
    linkedin_id = Column(String(255), unique=True, index=True)
    
    # Relationships
    organizations = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    created_jobs = relationship("Job", back_populates="created_by_user", foreign_keys="Job.created_by")
    comments = relationship("ApplicationNote", back_populates="user")
    interviews = relationship("InterviewParticipant", back_populates="user")
    activities = relationship("ApplicationActivity", back_populates="user")
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User {self.email}>"


class OrganizationMember(Base, TimeStampMixin):
    """Many-to-many relationship between Users and Organizations with roles."""
    
    __tablename__ = "organization_members"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RECRUITER)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default=dict)  # Custom permissions
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organizations")
    
    def __repr__(self):
        return f"<OrganizationMember {self.user_id} in {self.organization_id} as {self.role}>"
