"""Tests for candidate endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db


@pytest.mark.asyncio
async def test_list_candidates_unauthorized(client: AsyncClient):
    """Test listing candidates without authentication."""
    response = await client.get("/api/v1/candidates")
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

    response = await client.post("/api/v1/candidates", json=candidate_data)
    # Should require authentication
    assert response.status_code == 401