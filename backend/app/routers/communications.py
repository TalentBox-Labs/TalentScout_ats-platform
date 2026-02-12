"""
Communication and email management router.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.communication import EmailTemplate, Communication, EmailSequence, EmailSequenceStep
from app.models.candidate import Candidate
from app.middleware.auth import get_current_user
from app.schemas.communication import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    CommunicationCreate,
    CommunicationResponse,
    EmailSequenceCreate,
    EmailSequenceResponse,
    EmailSequenceEnrollRequest,
)
from app.services.email_service import EmailService
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/v1/communications", tags=["communications"])


@router.get("/email-templates", response_model=List[EmailTemplateResponse])
async def list_email_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all email templates for the organization.
    """
    result = await db.execute(
        select(EmailTemplate)
        .where(
            or_(
                EmailTemplate.organization_id == current_user.organization_id,
                EmailTemplate.is_system_template == True
            )
        )
        .order_by(EmailTemplate.created_at.desc())
    )
    templates = result.scalars().all()
    
    return templates


@router.post("/email-templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an email template.
    """
    new_template = EmailTemplate(
        name=template_data.name,
        subject=template_data.subject,
        body=template_data.body,
        template_type=template_data.template_type,
        variables=template_data.variables or [],
        organization_id=current_user.organization_id,
        is_system_template=False,
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return new_template


@router.patch("/email-templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: UUID,
    template_data: EmailTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an email template.
    """
    result = await db.execute(
        select(EmailTemplate).where(
            and_(
                EmailTemplate.id == template_id,
                EmailTemplate.organization_id == current_user.organization_id
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Update fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.post("/send", response_model=CommunicationResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_email(
    email_data: CommunicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send email to candidate.
    """
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(
            and_(
                Candidate.id == email_data.candidate_id,
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
    
    # Get template if template_id provided
    subject = email_data.subject
    body = email_data.body
    
    if email_data.template_id:
        template_result = await db.execute(
            select(EmailTemplate).where(EmailTemplate.id == email_data.template_id)
        )
        template = template_result.scalar_one_or_none()
        
        if template:
            subject = template.subject
            body = template.body
            
            # Replace variables
            if email_data.variables:
                for key, value in email_data.variables.items():
                    subject = subject.replace(f"{{{{{key}}}}}", str(value))
                    body = body.replace(f"{{{{{key}}}}}", str(value))
    
    # Use AI to enhance email if requested
    if email_data.use_ai_enhancement:
        ai_service = AIService()
        enhanced = await ai_service.enhance_email(body)
        body = enhanced.get("body", body)
    
    # Create communication record
    new_communication = Communication(
        candidate_id=email_data.candidate_id,
        application_id=email_data.application_id,
        template_id=email_data.template_id,
        subject=subject,
        body=body,
        channel="email",
        direction="outbound",
        status="queued",
        sent_by_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    
    db.add(new_communication)
    await db.commit()
    await db.refresh(new_communication)
    
    # Queue email sending in background
    email_service = EmailService()
    await email_service.send_email_async(
        to_email=candidate.email,
        subject=subject,
        body=body,
        communication_id=str(new_communication.id),
    )
    
    return new_communication


@router.get("", response_model=List[CommunicationResponse])
async def get_email_history(
    candidate_id: Optional[UUID] = Query(None),
    application_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get email history.
    """
    query = select(Communication).where(
        Communication.organization_id == current_user.organization_id
    )
    
    if candidate_id:
        query = query.where(Communication.candidate_id == candidate_id)
    if application_id:
        query = query.where(Communication.application_id == application_id)
    
    query = query.order_by(Communication.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    communications = result.scalars().all()
    
    return communications


@router.post("/email-sequences", response_model=EmailSequenceResponse, status_code=status.HTTP_201_CREATED)
async def create_email_sequence(
    sequence_data: EmailSequenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an email drip campaign sequence.
    """
    new_sequence = EmailSequence(
        name=sequence_data.name,
        description=sequence_data.description,
        trigger_event=sequence_data.trigger_event,
        is_active=True,
        organization_id=current_user.organization_id,
    )
    
    db.add(new_sequence)
    await db.flush()
    
    # Add steps
    for step_data in sequence_data.steps:
        step = EmailSequenceStep(
            sequence_id=new_sequence.id,
            template_id=step_data.template_id,
            delay_days=step_data.delay_days,
            order=step_data.order,
        )
        db.add(step)
    
    await db.commit()
    await db.refresh(new_sequence)
    
    return new_sequence


@router.post("/email-sequences/{sequence_id}/enroll", status_code=status.HTTP_202_ACCEPTED)
async def enroll_in_email_sequence(
    sequence_id: UUID,
    enroll_data: EmailSequenceEnrollRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll a candidate in an email sequence.
    """
    # Verify sequence exists
    result = await db.execute(
        select(EmailSequence).where(
            and_(
                EmailSequence.id == sequence_id,
                EmailSequence.organization_id == current_user.organization_id
            )
        )
    )
    sequence = result.scalar_one_or_none()
    
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email sequence not found",
        )
    
    # Verify candidate exists
    candidate_result = await db.execute(
        select(Candidate).where(
            and_(
                Candidate.id == enroll_data.candidate_id,
                Candidate.organization_id == current_user.organization_id
            )
        )
    )
    candidate = candidate_result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # TODO: Create enrollment record and schedule emails
    # This would involve creating scheduled tasks for each step in the sequence
    
    return {
        "message": f"Candidate enrolled in sequence '{sequence.name}'",
        "sequence_id": str(sequence_id),
        "candidate_id": str(enroll_data.candidate_id),
    }
