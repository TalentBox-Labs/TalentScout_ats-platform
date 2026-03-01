"""
Application pipeline management router with AI screening.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationActivity, ApplicationNote, ApplicationScore, ActivityType
from app.models.candidate import Candidate
from app.models.job import Job, JobStage
from app.middleware.auth import get_current_user
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListResponse,
    ApplicationStageUpdate,
    ApplicationStatusUpdate,
    NoteCreate,
    NoteResponse,
    ScoreCreate,
    ScoreResponse,
    ActivityResponse,
)
from app.workers.ai_screening import screen_candidate_task

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=List[ApplicationListResponse])
async def list_applications(
    job_id: Optional[UUID] = Query(None, description="Filter by job"),
    stage_id: Optional[UUID] = Query(None, description="Filter by stage"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List applications with filters.
    """
    query = (
        select(Application)
        .join(Job)
        .where(Job.organization_id == current_user.organization_id)
        .options(
            selectinload(Application.candidate),
            selectinload(Application.job).selectinload(Job.stages),
            selectinload(Application.current_stage_obj)
        )
    )
    
    # Apply filters
    if job_id:
        query = query.where(Application.job_id == job_id)
    if stage_id:
        query = query.where(Application.current_stage == stage_id)
    if status_filter:
        query = query.where(Application.status == status_filter)
    
    query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return applications


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an application (link candidate to job).
    Triggers AI screening in background.
    """
    # Verify candidate exists and belongs to organization
    result = await db.execute(
        select(Candidate).where(
            and_(
                Candidate.id == app_data.candidate_id,
                Candidate.organization_id == current_user.organization_id
            )
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Verify job exists and belongs to organization
    result = await db.execute(
        select(Job).where(
            and_(
                Job.id == app_data.job_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Check for duplicate application
    result = await db.execute(
        select(Application).where(
            and_(
                Application.candidate_id == app_data.candidate_id,
                Application.job_id == app_data.job_id
            )
        )
    )
    existing_app = result.scalar_one_or_none()
    
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application already exists for this candidate and job",
        )
    
    # Get the first stage of the job (Applied)
    result = await db.execute(
        select(JobStage).where(JobStage.job_id == app_data.job_id).order_by(JobStage.order)
    )
    first_stage = result.scalar_one_or_none()
    
    if not first_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has no pipeline stages configured",
        )
    
    # Create application
    new_application = Application(
        candidate_id=app_data.candidate_id,
        job_id=app_data.job_id,
        current_stage=first_stage.id if first_stage else None,
        status="active",
        source=app_data.source or "manual",
        cover_letter=app_data.cover_letter,
        organization_id=current_user.organization_id,
    )
    
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=new_application.id,
        activity_type=ActivityType.CREATED,
        title="Application Created",
        description="Application created",
        user_id=current_user.id,
    )
    db.add(activity)
    await db.commit()
    
    # Queue AI screening
    screen_candidate_task.delay(str(new_application.id))
    
    return new_application


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get application details with full timeline.
    """
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
        .options(
            selectinload(Application.candidate),
            selectinload(Application.job),
            selectinload(Application.current_stage_obj),
            selectinload(Application.activities),
            selectinload(Application.notes),
            selectinload(Application.scores)
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application
@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    app_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update application.
    """
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    # Update fields
    update_data = app_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    await db.commit()
    await db.refresh(application)
    
    return application

@router.patch("/{application_id}/stage", response_model=ApplicationResponse)
async def move_to_stage(
    application_id: UUID,
    stage_data: ApplicationStageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Move application to a different stage (logs activity).
    """
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    # Validate target stage belongs to the same job and organization
    result = await db.execute(
        select(JobStage)
        .join(Job)
        .where(
            and_(
                JobStage.id == stage_data.current_stage,
                Job.id == application.job_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    target_stage = result.scalar_one_or_none()
    
    if not target_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target stage not found or does not belong to this job",
        )
    
    old_stage_id = application.current_stage
    application.current_stage = stage_data.current_stage
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=application.id,
        activity_type=ActivityType.STAGE_CHANGED,
        title="Stage Changed",
        description=f"Moved to stage {stage_data.current_stage}",
        user_id=current_user.id,
        activity_metadata={"old_stage_id": str(old_stage_id), "new_stage_id": str(stage_data.current_stage)},
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(application)
    
    return application


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_status(
    application_id: UUID,
    status_data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update application status (hired, rejected, withdrawn, etc.).
    """
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    old_status = application.status
    application.status = status_data.status
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=application.id,
        activity_type=ActivityType.STATUS_CHANGED,
        title="Status Changed",
        description=f"Status changed from {old_status} to {status_data.status}",
        user_id=current_user.id,
        activity_metadata={"old_status": old_status, "new_status": status_data.status, "reason": status_data.reason},
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(application)
    
    return application


@router.post("/{application_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    application_id: UUID,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a note/comment to application (supports @mentions).
    """
    # Verify application exists
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    new_note = ApplicationNote(
        application_id=application_id,
        user_id=current_user.id,
        content=note_data.content,
        is_private=note_data.is_private,
    )
    
    db.add(new_note)
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=application_id,
        activity_type=ActivityType.NOTE_ADDED,
        title="Note Added",
        description=f"Note added by {current_user.first_name} {current_user.last_name}",
        user_id=current_user.id,
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(new_note)
    
    # TODO: Parse @mentions and send notifications
    
    return new_note


@router.get("/{application_id}/activities", response_model=List[ActivityResponse])
async def get_activities(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get activity timeline for an application.
    """
    # Verify application exists
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    # Get activities
    result = await db.execute(
        select(ApplicationActivity)
        .where(ApplicationActivity.application_id == application_id)
        .order_by(desc(ApplicationActivity.created_at))
    )
    activities = result.scalars().all()
    
    return activities


@router.post("/{application_id}/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def add_score(
    application_id: UUID,
    score_data: ScoreCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add manual scoring for an application.
    """
    # Verify application exists
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == application_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    new_score = ApplicationScore(
        application_id=application_id,
        user_id=current_user.id,
        category=score_data.category,
        score=score_data.score,
        max_score=score_data.max_score,
        notes=score_data.notes,
    )
    
    db.add(new_score)
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=application_id,
        activity_type=ActivityType.SCORE_UPDATED,
        title="Score Added",
        description=f"Score added: {score_data.category} - {score_data.score}/{score_data.max_score}",
        user_id=current_user.id,
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(new_score)
    
    return new_score