<<<<<<< HEAD
"""
Interview scheduling and management router.
"""
=======
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
from typing import List, Optional
from uuid import UUID
from datetime import datetime

<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewParticipant, InterviewFeedback
from app.models.application import Application
from app.models.job import Job
from app.middleware.auth import get_current_user
from app.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewListResponse,
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
    InterviewRescheduleRequest,
)

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])


@router.get("", response_model=List[InterviewListResponse])
async def list_interviews(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    application_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List interviews (calendar view data).
    """
    query = (
        select(Interview)
        .join(Application)
        .join(Job)
        .where(Job.organization_id == current_user.organization_id)
        .options(
            selectinload(Interview.application).selectinload(Application.candidate),
            selectinload(Interview.application).selectinload(Application.job),
            selectinload(Interview.participants)
        )
    )
    
    # Apply filters
    if start_date:
        query = query.where(Interview.scheduled_at >= start_date)
    if end_date:
        query = query.where(Interview.scheduled_at <= end_date)
    if application_id:
        query = query.where(Interview.application_id == application_id)
    
    query = query.order_by(Interview.scheduled_at.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    return interviews


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule an interview.
    """
    # Verify application exists
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == interview_data.application_id,
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
    
    new_interview = Interview(
        application_id=interview_data.application_id,
        scheduled_at=interview_data.scheduled_at,
        duration_minutes=interview_data.duration_minutes,
        interview_type=interview_data.interview_type,
        location=interview_data.location,
        meeting_link=interview_data.meeting_link,
        notes=interview_data.notes,
        status="scheduled",
    )
    
    db.add(new_interview)
    await db.flush()
    
    # Add participants
    for participant_id in interview_data.participant_ids:
        participant = InterviewParticipant(
            interview_id=new_interview.id,
            user_id=participant_id,
            role="interviewer",
        )
        db.add(participant)
    
    await db.commit()
    await db.refresh(new_interview)
    
    # TODO: Send calendar invites
    # TODO: Create calendar events in Google Calendar/Outlook
    
    return new_interview


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get interview details with participants and feedback.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
        .options(
            selectinload(Interview.application).selectinload(Application.candidate),
            selectinload(Interview.application).selectinload(Application.job),
            selectinload(Interview.participants),
            selectinload(Interview.feedback)
        )
    )
    interview = result.scalar_one_or_none()
=======
from ..database import get_db
from .. import models

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_interview(
    # interview_data: InterviewCreate,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Schedule a new interview
    """
    return {"message": "Create interview endpoint"}


@router.get("/")
async def list_interviews(
    application_id: Optional[UUID] = None,
    interviewer_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List interviews with optional filters
    """
    query = db.query(models.Interview)
    
    if application_id:
        query = query.filter(models.Interview.application_id == application_id)
    
    # Add more filters...
    
    interviews = query.offset(skip).limit(limit).all()
    return {"interviews": interviews}


@router.get("/{interview_id}")
async def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific interview by ID
    """
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id
    ).first()
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
<<<<<<< HEAD
            detail="Interview not found",
=======
            detail="Interview not found"
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
        )
    
    return interview


<<<<<<< HEAD
@router.patch("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: UUID,
    interview_data: InterviewUpdate,
    current_user: User = Depends(get_current_user),
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
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
=======
@router.put("/{interview_id}")
async def update_interview(
    interview_id: UUID,
    # interview_data: InterviewUpdate,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Update interview details
    """
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id
    ).first()
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
<<<<<<< HEAD
            detail="Interview not found",
        )
    
    # Update fields
    update_data = interview_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    await db.commit()
    await db.refresh(interview)
    
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
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
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
=======
            detail="Interview not found"
        )
    
    return {"message": "Update interview endpoint"}


@router.post("/{interview_id}/feedback")
async def add_interview_feedback(
    interview_id: UUID,
    # feedback_data: FeedbackCreate,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Add feedback for an interview
    """
    return {"message": "Add interview feedback endpoint"}


@router.get("/{interview_id}/feedback")
async def get_interview_feedback(
    interview_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get feedback for an interview
    """
    return {"message": "Get interview feedback endpoint"}


@router.post("/{interview_id}/generate-questions")
async def generate_interview_questions(
    interview_id: UUID,
    db: Session = Depends(get_db)
):
    """
    AI-generate interview questions based on job and candidate
    """
    return {"message": "AI interview question generation endpoint"}


@router.delete("/{interview_id}")
async def cancel_interview(
    interview_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Cancel an interview
    """
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id
    ).first()
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
<<<<<<< HEAD
            detail="Interview not found",
        )
    
    interview.status = "cancelled"
    await db.commit()
    
    # TODO: Send cancellation notifications
    # TODO: Delete calendar events
    
    return None


@router.post("/{interview_id}/reschedule", response_model=InterviewResponse)
async def reschedule_interview(
    interview_id: UUID,
    reschedule_data: InterviewRescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reschedule interview with notification.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    interview.scheduled_at = reschedule_data.new_scheduled_at
    interview.duration_minutes = reschedule_data.duration_minutes or interview.duration_minutes
    interview.location = reschedule_data.location or interview.location
    interview.meeting_link = reschedule_data.meeting_link or interview.meeting_link
    interview.status = "rescheduled"
    
    await db.commit()
    await db.refresh(interview)
    
    # TODO: Send reschedule notifications
    # TODO: Update calendar events
    
    return interview


@router.post("/{interview_id}/feedback", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_interview_feedback(
    interview_id: UUID,
    feedback_data: InterviewFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit interviewer feedback.
    """
    # Verify interview exists
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    new_feedback = InterviewFeedback(
        interview_id=interview_id,
        user_id=current_user.id,
        rating=feedback_data.rating,
        feedback_text=feedback_data.feedback_text,
        strengths=feedback_data.strengths,
        concerns=feedback_data.concerns,
        recommendation=feedback_data.recommendation,
    )
    
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    
    # Update interview status if all feedback collected
    # TODO: Check if all participants submitted feedback
    
    return new_feedback


@router.get("/{interview_id}/participants", response_model=List[dict])
async def get_interview_participants(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get interview participants.
    """
    result = await db.execute(
        select(Interview)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Interview.id == interview_id,
                Job.organization_id == current_user.organization_id
            )
        )
        .options(selectinload(Interview.participants))
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    return [
        {
            "id": str(p.id),
            "user_id": str(p.user_id),
            "role": p.role,
            "status": p.status,
        }
        for p in interview.participants
    ]
=======
            detail="Interview not found"
        )
    
    # TODO: Send cancellation notifications
    db.delete(interview)
    db.commit()
    
    return {"message": "Interview cancelled successfully"}
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
