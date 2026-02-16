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


@pytest.mark.asyncio
async def test_unpublish_job(client: TestClient, auth_headers: dict, test_job: dict):
    """Test unpublishing a job."""
    # First publish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200
    
    # Unpublish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/unpublish", headers=auth_headers)
    assert response.status_code == 200
    unpublished_job = response.json()
    assert unpublished_job["is_public"] is False


@pytest.mark.asyncio
async def test_track_share(client: TestClient, auth_headers: dict, test_job: dict):
    """Test tracking job shares."""
    # First publish the job to make it public
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200

    # Track a share
    share_data = {"platform": "linkedin"}
    response = client.post(
        f"/api/v1/jobs/{test_job['id']}/track-share",
        json=share_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Share tracked successfully"

    # Check that share count was incremented
    response = client.get(f"/api/v1/jobs/{test_job['id']}", headers=auth_headers)
    assert response.status_code == 200
    job = response.json()
    assert job["share_count"] == 1
    assert job["share_metadata"]["linkedin"] == 1


@pytest.mark.asyncio
async def test_track_multiple_shares(client: TestClient, auth_headers: dict, test_job: dict):
    """Test tracking multiple shares on different platforms."""
    # First publish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200

    # Track shares on different platforms
    platforms = ["linkedin", "twitter", "facebook", "linkedin"]  # linkedin twice

    for platform in platforms:
        share_data = {"platform": platform}
        response = client.post(
            f"/api/v1/jobs/{test_job['id']}/track-share",
            json=share_data,
            headers=auth_headers
        )
        assert response.status_code == 200

    # Check final counts
    response = client.get(f"/api/v1/jobs/{test_job['id']}", headers=auth_headers)
    assert response.status_code == 200
    job = response.json()
    assert job["share_count"] == 4
    assert job["share_metadata"]["linkedin"] == 2
    assert job["share_metadata"]["twitter"] == 1
    assert job["share_metadata"]["facebook"] == 1


@pytest.mark.asyncio
async def test_track_share_nonexistent_job(client: TestClient, auth_headers: dict):
    """Test tracking share for non-existent job."""
    share_data = {"platform": "linkedin"}
    response = client.post(
        "/api/v1/jobs/non-existent-id/track-share",
        json=share_data,
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_public_job_increments_view_count(client: TestClient, auth_headers: dict, test_job: dict):
    """Test that getting a public job increments view count."""
    # First publish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200
    published_job = response.json()

    # Get the public job (no auth required)
    response = client.get(f"/api/v1/jobs/public/{published_job['public_slug']}")
    assert response.status_code == 200
    public_job = response.json()
    assert public_job["view_count"] == 1

    # Get it again - view count should increment
    response = client.get(f"/api/v1/jobs/public/{published_job['public_slug']}")
    assert response.status_code == 200
    public_job = response.json()
    assert public_job["view_count"] == 2


@pytest.mark.asyncio
async def test_get_public_job_salary_visibility(client: TestClient, auth_headers: dict, test_job: dict):
    """Test salary visibility in public job endpoint."""
    # Update job with salary info
    update_data = {
        "salary_min": 50000,
        "salary_max": 70000,
        "salary_currency": "USD",
        "show_salary_public": True
    }
    response = client.patch(f"/api/v1/jobs/{test_job['id']}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    # Publish the job
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200
    published_job = response.json()

    # Get public job - salary should be visible
    response = client.get(f"/api/v1/jobs/public/{published_job['public_slug']}")
    assert response.status_code == 200
    public_job = response.json()
    assert public_job["salary_min"] == 50000
    assert public_job["salary_max"] == 70000
    assert public_job["salary_currency"] == "USD"

    # Update to hide salary
    update_data["show_salary_public"] = False
    response = client.patch(f"/api/v1/jobs/{test_job['id']}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    # Get public job - salary should be hidden
    response = client.get(f"/api/v1/jobs/public/{published_job['public_slug']}")
    assert response.status_code == 200
    public_job = response.json()
    assert public_job["salary_min"] is None
    assert public_job["salary_max"] is None
    assert public_job["salary_currency"] is None


@pytest.mark.asyncio
async def test_get_public_job_not_found(client: TestClient):
    """Test getting non-existent public job."""
    response = client.get("/api/v1/jobs/public/non-existent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_share_links(client: TestClient, auth_headers: dict, test_job: dict):
    """Test getting share links for a job."""
    # Publish the job first
    response = client.post(f"/api/v1/jobs/{test_job['id']}/publish-public", headers=auth_headers)
    assert response.status_code == 200
    published_job = response.json()

    # Get share links
    response = client.get(f"/api/v1/jobs/{test_job['id']}/share-links", headers=auth_headers)
    assert response.status_code == 200
    share_data = response.json()

    assert share_data["job_id"] == test_job["id"]
    assert share_data["job_title"] == test_job["title"]
    assert "public_url" in share_data
    assert "share_links" in share_data

    # Check share links structure
    share_links = share_data["share_links"]
    expected_platforms = ["linkedin", "twitter", "facebook", "email", "copy"]
    assert len(share_links) == len(expected_platforms)

    for link in share_links:
        assert link["platform"] in expected_platforms
        assert "url" in link
        assert "text" in link


@pytest.mark.asyncio
async def test_update_salary_visibility(client: TestClient, auth_headers: dict, test_job: dict):
    """Test updating salary visibility for public jobs."""
    # Update salary visibility
    visibility_data = {"show_salary_public": True}
    response = client.patch(
        f"/api/v1/jobs/{test_job['id']}/salary-visibility",
        json=visibility_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    job = response.json()
    assert job["show_salary_public"] is True

    # Update to hide salary
    visibility_data = {"show_salary_public": False}
    response = client.patch(
        f"/api/v1/jobs/{test_job['id']}/salary-visibility",
        json=visibility_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    job = response.json()
    assert job["show_salary_public"] is False