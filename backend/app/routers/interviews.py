"""
Interview management router.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewParticipant, InterviewFeedback, InterviewStatus
from app.models.application import Application, ApplicationActivity, ActivityType
from app.models.job import Job
from app.middleware.auth import get_current_membership, CurrentMembership
from app.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewListResponse,
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
    InterviewParticipantResponse,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    data: InterviewCreate,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule a new interview.
    """
    # Verify the application_id belongs to the org
    result = await db.execute(
        select(Application).join(Job).where(
            and_(
                Application.id == data.application_id,
                Job.organization_id == membership.organization_id
            )
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    
    # Create interview
    interview = Interview(
        title=data.title,
        application_id=str(data.application_id),
        interview_type=data.interview_type,
        scheduled_at=str(data.scheduled_at),
        duration_minutes=data.duration_minutes,
        description=data.description,
        timezone=data.timezone,
        location=data.location,
        meeting_link=data.meeting_link,
        meeting_id=data.meeting_id,
        meeting_password=data.meeting_password,
        instructions=data.instructions,
        notes=data.notes,
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    
    # Create participants
    participants = []
    for pid in data.participant_ids:
        participant = InterviewParticipant(
            interview_id=interview.id,
            user_id=str(pid),
        )
        participants.append(participant)
        db.add(participant)
    
    # Log activity
    activity = ApplicationActivity(
        activity_type=ActivityType.INTERVIEW_SCHEDULED,
        title="Interview Scheduled",
        user_id=membership.user.id,
        application_id=str(data.application_id),
    )
    db.add(activity)
    
    await db.commit()
    
    return interview


@router.get("", response_model=List[InterviewListResponse])
async def list_interviews(
    application_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    List interviews with optional filtering by application.
    """
    query = select(Interview).join(Application).join(Job).where(
        Job.organization_id == membership.organization_id
    )
    
    if application_id:
        query = query.where(Interview.application_id == str(application_id))
    
    query = query.order_by(Interview.scheduled_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    return interviews


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Get interview details with participants and feedback.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .options(selectinload(Interview.participants))
        .options(selectinload(Interview.feedback))
        .where(
            and_(
                Interview.id == str(interview_id),
                Job.organization_id == membership.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    return interview


@router.patch("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: UUID,
    data: InterviewUpdate,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Update interview details.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == str(interview_id),
                Job.organization_id == membership.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    await db.commit()
    await db.refresh(interview)
    
    return interview


@router.delete("/{interview_id}", response_model=InterviewResponse)
async def cancel_interview(
    interview_id: UUID,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel an interview.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == str(interview_id),
                Job.organization_id == membership.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    interview.status = InterviewStatus.CANCELLED
    await db.commit()
    await db.refresh(interview)
    
    return interview


@router.post("/{interview_id}/feedback", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    interview_id: UUID,
    data: InterviewFeedbackCreate,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback for an interview.
    """
    # Verify interview exists and belongs to org
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == str(interview_id),
                Job.organization_id == membership.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    # Create feedback
    feedback = InterviewFeedback(
        interview_id=str(interview_id),
        interviewer_id=str(membership.user.id),
        overall_rating=data.overall_rating,
        technical_rating=data.technical_rating,
        communication_rating=data.communication_rating,
        culture_fit_rating=data.culture_fit_rating,
        strengths=data.strengths,
        concerns=data.concerns,
        notes=data.notes,
        recommendation=data.recommendation,
        questions_answers=data.questions_answers or [],
        custom_ratings=data.custom_ratings or {},
        is_submitted=data.is_submitted,
    )
    
    if data.is_submitted:
        from datetime import datetime
        feedback.submitted_at = str(datetime.utcnow())
    
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/{interview_id}/feedback", response_model=List[InterviewFeedbackResponse])
async def list_feedback(
    interview_id: UUID,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    List all feedback for an interview.
    """
    # Verify interview exists and belongs to org
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == str(interview_id),
                Job.organization_id == membership.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    # Get feedback
    result = await db.execute(
        select(InterviewFeedback)
        .where(InterviewFeedback.interview_id == str(interview_id))
        .order_by(InterviewFeedback.created_at.desc())
    )
    feedback = result.scalars().all()
    
    return feedback