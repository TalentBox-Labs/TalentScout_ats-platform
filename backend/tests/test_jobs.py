"""Tests for job endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db


@pytest.fixture
async def client(db_session: AsyncSession):
    """Test client with database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_jobs_unauthorized(client: AsyncClient):
    """Test listing jobs without authentication."""
    response = await client.get("/jobs")
    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_job_unauthorized(client: AsyncClient):
    """Test creating job without authentication."""
    job_data = {
        "title": "Test Job",
        "description": "Test job description",
        "job_type": "full_time",
        "department": "Engineering"
    }

    response = await client.post("/jobs", json=job_data)
    # Should require authentication
    assert response.status_code == 401