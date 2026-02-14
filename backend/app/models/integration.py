"""Integration models."""
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class Integration(Base, TimeStampMixin):
    """Available integrations."""
    
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # "job_board", "calendar", "email", "video", "hris"
    icon_url = Column(String(500))
    
    # Configuration
    is_active = Column(Boolean, default=True)
    requires_oauth = Column(Boolean, default=False)
    requires_api_key = Column(Boolean, default=False)
    oauth_provider = Column(String(100))  # "google", "microsoft", "linkedin"
    
    # Documentation
    setup_instructions = Column(Text)
    docs_url = Column(String(500))
    
    # Relationships
    configs = relationship("IntegrationConfig", back_populates="integration")
    
    def __repr__(self):
        return f"<Integration {self.name}>"


class IntegrationConfig(Base, TimeStampMixin):
    """Organization-specific integration configuration."""
    
    __tablename__ = "integration_configs"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    integration_id = Column(UUID(as_uuid=False), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))  # User who set it up
    
    is_enabled = Column(Boolean, default=True)
    
    # OAuth Credentials
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    token_expires_at = Column(String(255))
    
    # API Keys
    api_key = Column(Text)  # Encrypted
    api_secret = Column(Text)  # Encrypted
    
    # Additional Config
    config_data = Column(JSON, default=dict)  # Provider-specific config
    
    # Status
    last_synced_at = Column(String(255))
    sync_status = Column(String(50))  # "success", "error", "pending"
    error_message = Column(Text)
    
    # Relationships
    integration = relationship("Integration", back_populates="configs")
    logs = relationship("IntegrationLog", back_populates="config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<IntegrationConfig {self.integration_id} for org {self.organization_id}>"


class IntegrationLog(Base, TimeStampMixin):
    """Integration sync logs."""
    
    __tablename__ = "integration_logs"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    config_id = Column(UUID(as_uuid=False), ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    
    action = Column(String(100), nullable=False)  # "sync", "post_job", "import_candidate"
    status = Column(String(50), nullable=False)  # "success", "error", "warning"
    
    # Details
    records_processed = Column(Integer, default=0)
    records_succeeded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    error_message = Column(Text)
    details = Column(JSON, default=dict)
    
    started_at = Column(String(255))
    completed_at = Column(String(255))
    
    # Relationships
    config = relationship("IntegrationConfig", back_populates="logs")
    
    def __repr__(self):
        return f"<IntegrationLog {self.action} - {self.status}>"
