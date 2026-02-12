<<<<<<< HEAD
"""
Job management router with AI-powered features.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.job import Job, JobStage, JobTemplate
from app.models.application import Application
from app.middleware.auth import get_current_user
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobStageCreate,
    JobStageUpdate,
    JobStageResponse,
    JobTemplateCreate,
    JobTemplateResponse,
)
from app.workers.embedding_worker import generate_job_embedding

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("", response_model=List[JobListResponse])
async def list_jobs(
    status_filter: Optional[str] = Query(None, description="Filter by status: draft, open, closed, on_hold"),
    department: Optional[str] = Query(None, description="Filter by department"),
    location: Optional[str] = Query(None, description="Filter by location"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all jobs with filtering and pagination.
    """
    query = select(Job).where(Job.organization_id == current_user.organization_id)
    
    # Apply filters
    if status_filter:
        query = query.where(Job.status == status_filter)
    if department:
        query = query.where(Job.department.ilike(f"%{department}%"))
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    
    # Order by created date descending
    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    # Get application counts for each job
    job_responses = []
    for job in jobs:
        app_count_query = select(func.count(Application.id)).where(Application.job_id == job.id)
        app_count_result = await db.execute(app_count_query)
        app_count = app_count_result.scalar()
        
        job_data = JobListResponse.model_validate(job)
        job_data.applications_count = app_count
        job_responses.append(job_data)
    
    return job_responses


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new job posting with automatic embedding generation.
    """
    new_job = Job(
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        responsibilities=job_data.responsibilities,
        department=job_data.department,
        location=job_data.location,
        employment_type=job_data.employment_type,
        experience_level=job_data.experience_level,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        salary_currency=job_data.salary_currency,
        skills_required=job_data.skills_required or [],
        status="draft",
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Queue embedding generation in background (Celery worker)
    generate_job_embedding.delay(str(new_job.id))
    
    # Create default pipeline stages
    default_stages = [
        {"name": "Applied", "order": 1, "type": "application"},
        {"name": "Screening", "order": 2, "type": "screening"},
        {"name": "Interview", "order": 3, "type": "interview"},
        {"name": "Offer", "order": 4, "type": "offer"},
        {"name": "Hired", "order": 5, "type": "hired"},
    ]
    
    for stage_data in default_stages:
        stage = JobStage(
            job_id=new_job.id,
            name=stage_data["name"],
            order=stage_data["order"],
            stage_type=stage_data["type"],
        )
        db.add(stage)
    
    await db.commit()
    
    return new_job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get job details with applications count.
    """
    result = await db.execute(
        select(Job)
        .where(and_(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ))
        .options(selectinload(Job.stages))
    )
    job = result.scalar_one_or_none()
    
=======
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
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
<<<<<<< HEAD
    
=======
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
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
<<<<<<< HEAD
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update job details.
    """
    result = await db.execute(
        select(Job).where(and_(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    # Regenerate embeddings if critical fields changed
    if any(field in update_data for field in ['title', 'description', 'requirements', 'skills_required']):
        generate_job_embedding.delay(str(job.id))
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a job (sets status to closed).
    """
    result = await db.execute(
        select(Job).where(and_(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    job.status = "closed"
    await db.commit()
    
    return None


@router.post("/{job_id}/publish", response_model=JobResponse)
async def publish_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Publish a job (change status from draft to open).
    """
    result = await db.execute(
        select(Job).where(and_(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    if job.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft jobs can be published",
        )
    
    job.status = "open"
    await db.commit()
    await db.refresh(job)
    
    return job


@router.post("/{job_id}/stages", response_model=JobStageResponse, status_code=status.HTTP_201_CREATED)
async def create_job_stage(
    job_id: UUID,
    stage_data: JobStageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a custom pipeline stage for a job.
    """
    # Verify job exists and user has access
    result = await db.execute(
        select(Job).where(and_(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    new_stage = JobStage(
        job_id=job_id,
        name=stage_data.name,
        order=stage_data.order,
        stage_type=stage_data.stage_type,
    )
    
    db.add(new_stage)
    await db.commit()
    await db.refresh(new_stage)
    
    return new_stage


@router.patch("/{job_id}/stages/{stage_id}", response_model=JobStageResponse)
async def update_job_stage(
    job_id: UUID,
    stage_id: UUID,
    stage_data: JobStageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a pipeline stage (order or settings).
    """
    result = await db.execute(
        select(JobStage)
        .join(Job)
        .where(and_(
            JobStage.id == stage_id,
            JobStage.job_id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found",
        )
    
    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)
    
    await db.commit()
    await db.refresh(stage)
    
    return stage


@router.delete("/{job_id}/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_stage(
    job_id: UUID,
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a custom pipeline stage.
    """
    result = await db.execute(
        select(JobStage)
        .join(Job)
        .where(and_(
            JobStage.id == stage_id,
            JobStage.job_id == job_id,
            Job.organization_id == current_user.organization_id
        ))
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found",
        )
    
    await db.delete(stage)
    await db.commit()
    
    return None


# Job Templates endpoints
@router.get("/templates/list", response_model=List[JobTemplateResponse])
async def list_job_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all job templates for the organization.
    """
    result = await db.execute(
        select(JobTemplate).where(
            or_(
                JobTemplate.organization_id == current_user.organization_id,
                JobTemplate.is_public == True
            )
        ).order_by(JobTemplate.created_at.desc())
    )
    templates = result.scalars().all()
    
    return templates


@router.post("/templates", response_model=JobTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_job_template(
    template_data: JobTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a job template.
    """
    new_template = JobTemplate(
        name=template_data.name,
        title=template_data.title,
        description=template_data.description,
        requirements=template_data.requirements,
        responsibilities=template_data.responsibilities,
        department=template_data.department,
        employment_type=template_data.employment_type,
        experience_level=template_data.experience_level,
        skills_required=template_data.skills_required or [],
        is_public=False,
        organization_id=current_user.organization_id,
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return new_template


@router.post("/from-template/{template_id}", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a job from a template.
    """
    result = await db.execute(
        select(JobTemplate).where(
            and_(
                JobTemplate.id == template_id,
                or_(
                    JobTemplate.organization_id == current_user.organization_id,
                    JobTemplate.is_public == True
                )
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    new_job = Job(
        title=template.title,
        description=template.description,
        requirements=template.requirements,
        responsibilities=template.responsibilities,
        department=template.department,
        employment_type=template.employment_type,
        experience_level=template.experience_level,
        skills_required=template.skills_required,
        status="draft",
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Queue embedding generation
    generate_job_embedding.delay(str(new_job.id))
    
    return new_job
=======
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
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
