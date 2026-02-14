"""Tests for candidate endpoints."""
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
async def test_list_candidates_unauthorized(client: AsyncClient):
    """Test listing candidates without authentication."""
    response = await client.get("/candidates")
    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_candidate_unauthorized(client: AsyncClient):
    """Test creating candidate without authentication."""
    candidate_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }

    response = await client.post("/candidates", json=candidate_data)
    # Should require authentication
    assert response.status_code == 401