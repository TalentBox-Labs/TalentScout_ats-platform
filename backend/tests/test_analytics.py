"""Tests for analytics endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.main import app
from app.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.models.job import Job
from app.utils.security import create_access_token
from datetime import datetime, timedelta


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
async def test_user_with_org(db_session: AsyncSession):
    """Create a test user with organization."""
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
        user_id=user.id,
        organization_id=org.id,
        role=UserRole.ADMIN
    )
    db_session.add(member)
    await db_session.commit()

    return user, org


@pytest.fixture
async def auth_headers(test_user_with_org):
    """Create authentication headers."""
    user, org = test_user_with_org
    token = create_access_token({"sub": user.id, "org_id": org.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def public_jobs(db_session: AsyncSession, test_user_with_org):
    """Create test public jobs with analytics data."""
    user, org = test_user_with_org

    jobs = []
    for i in range(3):
        job = Job(
            organization_id=org.id,
            created_by=user.id,
            title=f"Test Public Job {i+1}",
            description=f"Description for job {i+1}",
            is_public=True,
            public_slug=f"test-job-{i+1}",
            view_count=10 * (i+1),  # 10, 20, 30 views
            share_count=2 * (i+1),  # 2, 4, 6 shares
            share_metadata={"linkedin": i+1, "twitter": i+1, "facebook": i+1},
            published_at=datetime.utcnow() - timedelta(days=i*5)  # Different publish dates
        )
        db_session.add(job)
        jobs.append(job)

    await db_session.commit()

    # Refresh to get IDs
    for job in jobs:
        await db_session.refresh(job)

    return jobs


class TestAnalytics:
    """Test analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_analytics_overview(self, client: AsyncClient, auth_headers, public_jobs):
        """Test getting analytics overview."""
        response = await client.get("/api/v1/analytics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Check that we have the expected keys
        assert "totalApplications" in data
        assert "totalJobs" in data
        assert "avgTimeToHire" in data
        assert "conversionRate" in data
        assert "applicationsByStage" in data
        assert "applicationsByJob" in data
        assert "monthlyApplications" in data

    @pytest.mark.asyncio
    async def test_get_public_jobs_analytics(self, client: AsyncClient, auth_headers, public_jobs):
        """Test getting public jobs analytics."""
        response = await client.get("/api/v1/analytics/public-jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Check overview metrics
        assert "overview" in data
        overview = data["overview"]
        assert overview["totalPublicJobs"] == 3
        assert overview["totalViews"] == 60  # 10+20+30
        assert overview["totalShares"] == 12  # 2+4+6

        # Check top jobs by views
        assert "topJobsByViews" in data
        top_jobs = data["topJobsByViews"]
        assert len(top_jobs) == 3
        # Should be ordered by views descending
        assert top_jobs[0]["views"] >= top_jobs[1]["views"]
        assert top_jobs[1]["views"] >= top_jobs[2]["views"]

        # Check share by platform
        assert "shareByPlatform" in data
        share_by_platform = data["shareByPlatform"]
        assert len(share_by_platform) == 3  # linkedin, twitter, facebook
        # Each platform should have 1+2+3 = 6 shares
        for platform_data in share_by_platform:
            assert platform_data["shares"] == 6

        # Check engagement over time
        assert "engagementOverTime" in data
        engagement = data["engagementOverTime"]
        assert len(engagement) == 30  # Last 30 days

    @pytest.mark.asyncio
    async def test_get_job_analytics(self, client: AsyncClient, auth_headers, public_jobs):
        """Test getting analytics for a specific job."""
        job = public_jobs[0]  # First job with 10 views, 2 shares

        response = await client.get(f"/api/v1/analytics/public-jobs/{job.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["jobId"] == job.id
        assert data["title"] == job.title
        assert "metrics" in data
        assert data["metrics"]["views"] == 10
        assert data["metrics"]["shares"] == 2

        # Check share distribution
        assert "shareDistribution" in data
        share_dist = data["shareDistribution"]
        assert len(share_dist) == 3  # 3 platforms
        for platform_data in share_dist:
            assert platform_data["count"] == 1  # Each platform has 1 share for this job
            assert platform_data["percentage"] == 33.3  # 1/3 ≈ 33.3%

    @pytest.mark.asyncio
    async def test_get_job_analytics_not_found(self, client: AsyncClient, auth_headers):
        """Test getting analytics for non-existent job."""
        response = await client.get("/api/v1/analytics/public-jobs/non-existent-id", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_job_analytics_private_job(self, client: AsyncClient, auth_headers, db_session, test_user_with_org):
        """Test getting analytics for private job (should fail)."""
        user, org = test_user_with_org

        # Create a private job
        private_job = Job(
            organization_id=org.id,
            created_by=user.id,
            title="Private Job",
            description="Private job description",
            is_public=False
        )
        db_session.add(private_job)
        await db_session.commit()
        await db_session.refresh(private_job)

        response = await client.get(f"/api/v1/analytics/public-jobs/{private_job.id}", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_analytics_without_auth(self, client: AsyncClient):
        """Test analytics endpoints require authentication."""
        endpoints = [
            "/api/v1/analytics",
            "/api/v1/analytics/public-jobs",
            "/api/v1/analytics/public-jobs/some-id"
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401