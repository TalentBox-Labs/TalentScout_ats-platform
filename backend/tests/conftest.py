"""Test configuration and fixtures."""
import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, test_db_session, _test_session
from app.config import settings

# Set testing mode
os.environ['TESTING'] = 'true'

# Import all models to register them with Base
import app.models
from app.models.job import Job  # Ensure Job is imported

# Global variable for test session
test_session = None
from app.models import Job as JobModel  # Also import as JobModel


@pytest.fixture
async def client(db_session: AsyncSession):
    """Test client with database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()