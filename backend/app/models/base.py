"""Base models and mixins."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String


class TimeStampMixin:
    """Mixin to add created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4())
