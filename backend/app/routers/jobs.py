from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.job import Job, JobStage, JobStatus
from ..models.application import Application
from ..models.user import User, OrganizationMember
from ..schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobStageCreate,
    JobStageResponse,
    JobApplicationSummary,
)
from .auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


async def _get_user_org_id(current_user: User, db: AsyncSession) -> str:
    """
    Helper to get the active organization ID for the current user.
    """
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    )
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any active organization",
        )
    return str(org_member.organization_id)


async def _get_job_for_org(
    job_id: UUID,
    org_id: str,
    db: AsyncSession,
) -> Job:
    """
    Fetch a job by ID scoped to the given organization.
    """
    result = await db.execute(
        select(Job).where(
            Job.id == str(job_id),
            Job.organization_id == org_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new job posting for the current user's organization.
    """
    org_id = await _get_user_org_id(current_user, db)

    job = Job(
        organization_id=org_id,
        created_by=current_user.id,
        **job_data.model_dump(exclude_unset=True),
    )

    db.add(job)
    await db.flush()
    await db.refresh(job)

    return job


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List job postings for the current user's organization.
    """
    org_id = await _get_user_org_id(current_user, db)

    stmt = (
        select(Job)
        .where(Job.organization_id == org_id)
        .offset(skip)
        .limit(limit)
        .order_by(Job.created_at.desc())
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific job by ID for the current user's organization.
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a job posting.
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)

    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.flush()
    await db.refresh(job)

    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a job posting.
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)

    db.delete(job)

    # Commit is handled by the session dependency, so we just return 204.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{job_id}/stages",
    response_model=JobStageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_job_stage(
    job_id: UUID,
    stage_data: JobStageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a pipeline stage to a job.
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)

    order = stage_data.order
    if order is None:
      result = await db.execute(
          select(func.max(JobStage.order)).where(JobStage.job_id == job.id)
      )
      max_order = result.scalar_one_or_none()
      order = (max_order or 0) + 1

    stage = JobStage(
        job_id=job.id,
        name=stage_data.name,
        description=stage_data.description,
        order=order,
        color=stage_data.color,
        is_system=stage_data.is_system,
        auto_reject_days=stage_data.auto_reject_days,
        settings=stage_data.settings,
    )

    db.add(stage)
    await db.flush()
    await db.refresh(stage)

    return stage


@router.get(
    "/{job_id}/applications",
    response_model=List[JobApplicationSummary],
)
async def get_job_applications(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all applications for a specific job.
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)

    stmt = select(Application).where(Application.job_id == job.id)
    result = await db.execute(stmt)
    applications = result.scalars().all()

    return applications


@router.post(
    "/{job_id}/publish",
    response_model=JobResponse,
)
async def publish_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Publish a job (set status to OPEN).
    """
    org_id = await _get_user_org_id(current_user, db)
    job = await _get_job_for_org(job_id, org_id, db)

    if job.status == JobStatus.OPEN:
        return job

    job.status = JobStatus.OPEN
    await db.flush()
    await db.refresh(job)

    return job


@router.post("/{job_id}/generate-description")
async def generate_job_description(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-generate job description (placeholder for future AI integration).
    """
    # TODO: Integrate with AI service to generate a richer description
    # based on job requirements, responsibilities, and skills.
    org_id = await _get_user_org_id(current_user, db)
    await _get_job_for_org(job_id, org_id, db)

    return {"message": "AI job description generation endpoint"}
