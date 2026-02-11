"""Communication and email models."""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class CommunicationType(str, enum.Enum):
    """Communication type enum."""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class CommunicationStatus(str, enum.Enum):
    """Communication status enum."""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"


class EmailTemplate(Base, TimeStampMixin):
    """Email template model."""
    
    __tablename__ = "email_templates"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)  # HTML content
    
    # Template Variables
    variables = Column(JSON, default=list)  # List of available variables like {{candidate_name}}
    
    # Categorization
    category = Column(String(100))  # e.g., "rejection", "interview_invite", "offer"
    stage = Column(String(100))  # Pipeline stage this is for
    
    # Settings
    is_public = Column(Boolean, default=False)  # Shared across organization
    is_ai_generated = Column(Boolean, default=False)
    tone = Column(String(50))  # "professional", "friendly", "casual"
    
    # Relationships
    communications = relationship("Communication", back_populates="template")
    
    def __repr__(self):
        return f"<EmailTemplate {self.name}>"


class Communication(Base, TimeStampMixin):
    """Communication log - emails, SMS, etc."""
    
    __tablename__ = "communications"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=False), ForeignKey("candidates.id", ondelete="CASCADE"))
    application_id = Column(UUID(as_uuid=False), ForeignKey("applications.id", ondelete="SET NULL"))
    template_id = Column(UUID(as_uuid=False), ForeignKey("email_templates.id", ondelete="SET NULL"))
    sent_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Communication Details
    type = Column(SQLEnum(CommunicationType), nullable=False, default=CommunicationType.EMAIL)
    status = Column(SQLEnum(CommunicationStatus), nullable=False, default=CommunicationStatus.DRAFT, index=True)
    
    # Email Fields
    to_email = Column(String(255))
    from_email = Column(String(255))
    cc = Column(JSON, default=list)
    bcc = Column(JSON, default=list)
    subject = Column(String(500))
    body = Column(Text)  # HTML content
    
    # SMS Fields
    to_phone = Column(String(20))
    sms_body = Column(Text)
    
    # Tracking
    sent_at = Column(String(255))
    delivered_at = Column(String(255))
    opened_at = Column(String(255))
    clicked_at = Column(String(255))
    
    # Metadata
    provider_message_id = Column(String(255))  # SendGrid/Resend message ID
    error_message = Column(Text)
    attachments = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    template = relationship("EmailTemplate", back_populates="communications")
    
    def __repr__(self):
        return f"<Communication {self.type} to {self.to_email or self.to_phone}>"


class EmailSequence(Base, TimeStampMixin):
    """Automated email sequence/drip campaign."""
    
    __tablename__ = "email_sequences"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Sequence Configuration
    trigger_event = Column(String(100))  # e.g., "application_created", "stage_changed"
    trigger_stage = Column(String(100))  # Specific stage if applicable
    
    # Emails in Sequence
    emails = Column(JSON, nullable=False)  # List of emails with delays
    # Format: [{"template_id": "...", "delay_days": 0}, {"template_id": "...", "delay_days": 3}]
    
    # Statistics
    total_enrolled = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<EmailSequence {self.name}>"
