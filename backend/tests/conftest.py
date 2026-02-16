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


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    # Use SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Set the test session in context and global
        test_db_session.set(session)
        global test_session
        test_session = session
        # Set the global in database module
        from app.database import _test_session
        _test_session = session
        
        # Set dependency override globally
        from app.main import app
        from app.database import get_db
        
        async def override_get_db():
            yield session
        
        app.dependency_overrides[get_db] = override_get_db
        
        yield session
        # Clear the context and global
        test_db_session.set(None)
        test_session = None
        _test_session = None
        # Clear dependency override
        app.dependency_overrides.clear()
        # Rollback any changes after test
        await session.rollback()