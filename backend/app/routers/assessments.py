"""
Assessment and screening templates router.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.assessment import ScreeningTemplate, Assessment, AssessmentResponse, AssessmentStatus
from app.models.application import Application
from app.models.job import Job
from app.middleware.auth import get_current_user
from app.schemas.assessment import (
    ScreeningTemplateCreate,
    ScreeningTemplateUpdate,
    ScreeningTemplateResponse,
    ScreeningQuestionCreate,
    AssessmentCreate,
    AssessmentResponse as AssessmentResponseSchema,
    AssessmentResponseCreate,
    AssessmentResponseResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("/templates", response_model=List[ScreeningTemplateResponse])
async def list_screening_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all screening templates for the organization.
    """
    result = await db.execute(
        select(ScreeningTemplate)
        .where(ScreeningTemplate.organization_id == current_user.organization_id)
        .options(selectinload(ScreeningTemplate.questions))
        .order_by(ScreeningTemplate.created_at.desc())
    )
    templates = result.scalars().all()
    
    return templates


@router.post("/templates", response_model=ScreeningTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_screening_template(
    template_data: ScreeningTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a screening template.
    """
    new_template = ScreeningTemplate(
        name=template_data.name,
        description=template_data.description,
        questions=[q.model_dump() for q in template_data.questions],  # Store as JSON
        organization_id=current_user.organization_id,
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return new_template


@router.get("/templates/{template_id}", response_model=ScreeningTemplateResponse)
async def get_screening_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get screening template details.
    """
    result = await db.execute(
        select(ScreeningTemplate)
        .where(
            and_(
                ScreeningTemplate.id == template_id,
                ScreeningTemplate.organization_id == current_user.organization_id
            )
        )
        .options(selectinload(ScreeningTemplate.questions))
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    return template


@router.patch("/templates/{template_id}", response_model=ScreeningTemplateResponse)
async def update_screening_template(
    template_id: UUID,
    template_data: ScreeningTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update screening template.
    """
    result = await db.execute(
        select(ScreeningTemplate).where(
            and_(
                ScreeningTemplate.id == template_id,
                ScreeningTemplate.organization_id == current_user.organization_id
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


@router.post("", response_model=AssessmentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an assessment for an application.
    """
    # Verify application exists
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            and_(
                Application.id == assessment_data.application_id,
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
    
    # Verify template exists
    result = await db.execute(
        select(ScreeningTemplate).where(
            and_(
                ScreeningTemplate.id == assessment_data.template_id,
                ScreeningTemplate.organization_id == current_user.organization_id
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    new_assessment = Assessment(
        application_id=assessment_data.application_id,
        template_id=assessment_data.template_id,
        title=assessment_data.title or "Assessment",
        status=AssessmentStatus.PENDING,
    )
    
    db.add(new_assessment)
    await db.commit()
    await db.refresh(new_assessment)
    
    return new_assessment


@router.get("/{assessment_id}", response_model=AssessmentResponseSchema)
async def get_assessment(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get assessment details with responses.
    """
    result = await db.execute(
        select(Assessment)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Assessment.id == assessment_id,
                Job.organization_id == current_user.organization_id
            )
        )
        .options(
            selectinload(Assessment.template),
            selectinload(Assessment.responses)
        )
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    return assessment


@router.post("/{assessment_id}/responses", response_model=AssessmentResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_assessment_responses(
    assessment_id: UUID,
    response_data: AssessmentResponseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit candidate responses to assessment.
    """
    # Verify assessment exists
    result = await db.execute(
        select(Assessment)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Assessment.id == assessment_id,
                Job.organization_id == current_user.organization_id
            )
        )
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    new_response = AssessmentResponse(
        assessment_id=assessment_id,
        question_id=response_data.question_id,
        response_text=response_data.response_text,
    )
    
    db.add(new_response)
    await db.commit()
    await db.refresh(new_response)
    
    return new_response


@router.post("/{assessment_id}/score", response_model=AssessmentResponseSchema)
async def score_assessment(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI scoring of assessment responses.
    """
    # Fetch assessment with responses
    result = await db.execute(
        select(Assessment)
        .join(Application)
        .join(Job)
        .where(
            and_(
                Assessment.id == assessment_id,
                Job.organization_id == current_user.organization_id
            )
        )
        .options(
            selectinload(Assessment.template).selectinload(ScreeningTemplate.questions),
            selectinload(Assessment.responses)
        )
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    
    # Use AI to score responses
    ai_service = AIService()
    
    total_score = 0
    max_score = 0
    
    for response in assessment.responses:
        # Find corresponding question
        question = next((q for q in assessment.template.questions if q['id'] == response.question_id), None)
        
        if question:
            max_score += question.get('points', 0)
            
            if question.get('question_type') == "multiple_choice" and question.get('correct_answer'):
                # Auto-score multiple choice
                if response.response_text == question.get('correct_answer'):
                    response.score = question.get('points', 0)
                    total_score += question.get('points', 0)
                else:
                    response.score = 0
            else:
                # Use AI to score open-ended questions
                score_result = await ai_service.score_assessment_response(
                    question=question.get('question_text', ''),
                    response=response.response_text,
                    max_points=question.get('points', 10),
                )
                response.score = score_result.get("score", 0)
                response.feedback = score_result.get("feedback")
                total_score += response.score
    
    # Update assessment
    assessment.total_score = total_score
    assessment.max_score = max_score
    assessment.status = "completed"
    
    await db.commit()
    await db.refresh(assessment)
    
    return assessment
