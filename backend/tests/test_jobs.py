"""Tests for job endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.models.job import Job
from app.utils.security import create_access_token


@pytest.fixture
def client(db_session: AsyncSession):
    """Test client with database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = AsyncClient(app=app, base_url="http://testserver")
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user with organization."""
    # Create organization first
    from app.models.user import Organization, OrganizationMember, UserRole
    org = Organization(
        name="Test Organization",
        domain="test.com"
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    # Create user
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create organization membership
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=UserRole.ADMIN
    )
    db_session.add(member)
    await db_session.commit()
    
    return user


@pytest.fixture
async def auth_headers(test_user, db_session: AsyncSession):
    """Create authentication headers."""
    # Get user's organization
    from app.models.user import OrganizationMember
    result = await db_session.execute(
        OrganizationMember.__table__.select().where(OrganizationMember.user_id == test_user.id)
    )
    member_row = result.first()
    org_id = str(member_row.organization_id) if member_row else None
    
    token = create_access_token(data={"sub": str(test_user.id), "org_id": org_id})
    yield {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_job(db_session: AsyncSession, test_user):
    """Create a test job."""
    # Get the user's organization
    from app.models.user import OrganizationMember
    member = await db_session.execute(
        OrganizationMember.__table__.select().where(OrganizationMember.user_id == test_user.id)
    )
    member_row = member.first()
    org_id = member_row.organization_id
    
    job = Job(
        title="Test Job",
        description="Test job description",
        job_type="full_time",
        status="open",
        organization_id=org_id,
        created_by=test_user.id
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    yield {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "job_type": job.job_type,
        "status": job.status
    }


@pytest.fixture
def client(db_session: AsyncSession):
    """Test client with database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_list_jobs_unauthorized(client: TestClient):
    """Test listing jobs without authentication."""
    response = client.get("/api/v1/jobs")
    # Should require authentication
    assert response.status_code == 401


def test_create_job_unauthorized(client: TestClient):
    """Test creating job without authentication."""
    job_data = {
        "title": "Test Job",
        "description": "Test job description",
        "job_type": "full_time",
        "department": "Engineering"
    }

    response = client.post("/api/v1/jobs", json=job_data)
    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_publish_job_public(db_session: AsyncSession):
    """Test publishing a job publicly."""
    from app.models.user import User, Organization, OrganizationMember, UserRole
    from app.models.job import Job
    
    # Create organization
    org = Organization(
        name="Test Organization",
        domain="test.com"
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    # Create user
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create organization membership
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=UserRole.ADMIN
    )
    db_session.add(member)
    await db_session.commit()
    
    # Create job
    job = Job(
        title="Test Job",
        description="Test job description",
        job_type="full_time",
        status="open",
        organization_id=org.id,
        created_by=user.id
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    # Test the slug generation
    await job.generate_slug(db_session)
    
    # Test publishing
    job.is_public = True
    from datetime import datetime
    job.published_at = datetime.utcnow()
    
    await db_session.commit()
    await db_session.refresh(job)
    
    assert job.is_public is True
    assert job.public_slug is not None
    assert job.published_at is not None


def test_unpublish_job(client: TestClient, auth_headers: dict, test_job: dict):
    """Test unpublishing a job."""
    # First publish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200
    
    # Unpublish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/unpublish", headers=auth_headers)
    assert response.status_code == 200
    unpublished_job = response.json()
    assert unpublished_job["is_public"] is False