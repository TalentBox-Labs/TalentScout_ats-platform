"""
AI router for AI-powered features like resume parsing, candidate matching, etc.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationActivity, ActivityType
from app.models.candidate import Candidate
from app.models.job import Job
from app.middleware.auth import get_current_user
from app.services.ai_service import AIService
from app.services.parser_service import ParserService
from app.workers.ai_screening import screen_candidate_task
from app.workers.resume_parser import parse_resume_task
from app.schemas.ai import EmailGenerationRequest

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/parse-resume", response_model=Dict[str, Any])
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Parse a resume file and extract candidate information using AI.
    """
    try:
        # Read file content
        file_content = await file.read()
        content_type = file.content_type or "application/pdf"
        
        # Extract text using ParserService
        parser = ParserService()
        resume_text = await parser.extract_text_from_bytes(file_content, content_type)
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume file"
            )
        
        # Parse with AI
        ai_service = AIService()
        parsed_data = await ai_service.parse_resume_text(resume_text)
        
        # Generate embedding for semantic search
        embedding = await ai_service.generate_embedding(resume_text)
        
        return {
            "parsed_data": parsed_data,
            "embedding": embedding,
            "confidence": 0.85,  # Placeholder - could be calculated
            "text_length": len(resume_text),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume parsing failed: {str(e)}"
        )


@router.post("/screen/{application_id}", response_model=Dict[str, Any])
async def screen_candidate(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Run AI screening for a candidate application.
    """
    # Verify application exists and belongs to user's organization
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            Application.id == application_id,
            Job.organization_id == current_user.organization_id
        )
        .options(
            selectinload(Application.candidate),
            selectinload(Application.job)
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )
    
    # Queue AI screening task
    screen_candidate_task.delay(str(application_id))
    
    return {
        "message": "AI screening started",
        "application_id": str(application_id),
        "status": "processing"
    }


@router.post("/match-candidates", response_model=Dict[str, Any])
async def match_candidates(
    job_id: UUID,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Match candidates to a job using semantic search.
    """
    # Verify job exists and belongs to user's organization
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.organization_id == current_user.organization_id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Generate embedding for job description
    ai_service = AIService()
    job_text = f"{job.title} {job.description or ''} {job.requirements or ''}"
    job_embedding = await ai_service.generate_embedding(job_text)
    
    # Perform vector similarity search
    query = text("""
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.current_position,
            c.current_company,
            c.location,
            c.resume_url,
            1 - (c.resume_embedding <=> :job_embedding::vector) as similarity_score
        FROM candidates c
        WHERE c.organization_id = :org_id
            AND c.resume_embedding IS NOT NULL
        ORDER BY c.resume_embedding <=> :job_embedding::vector
        LIMIT :limit_val
    """)
    
    result = await db.execute(query, {
        "job_embedding": job_embedding,
        "org_id": str(current_user.organization_id),
        "limit_val": limit
    })
    candidates = result.fetchall()
    
    # Format results
    matches = []
    for row in candidates:
        if row.similarity_score >= 0.5:  # Minimum threshold
            matches.append({
                "candidate_id": str(row.id),
                "name": f"{row.first_name} {row.last_name}",
                "email": row.email,
                "current_position": row.current_position,
                "current_company": row.current_company,
                "location": row.location,
                "similarity_score": float(row.similarity_score),
                "match_percentage": round(float(row.similarity_score) * 100, 1)
            })
    
    return {
        "job_id": str(job_id),
        "matches": matches,
        "total_matches": len(matches)
    }


@router.post("/generate-email", response_model=Dict[str, Any])
async def generate_email(
    request: EmailGenerationRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate personalized email content using AI.
    """
    ai_service = AIService()
    
    email_content = await ai_service.generate_email(
        context=request.context,
        email_type=request.template_type,
        tone=request.tone
    )
    
    return {
        "subject": email_content.get("subject", ""),
        "body": email_content.get("body", ""),
        "template_type": request.template_type,
        "tone": request.tone
    }


@router.post("/generate-job-description", response_model=Dict[str, Any])
async def generate_job_description(
    title: str = Form(...),
    department: Optional[str] = Form(None),
    experience_level: Optional[str] = Form("mid"),
    skills: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a complete job description using AI.
    """
    ai_service = AIService()
    
    job_description = await ai_service.generate_job_description(
        title=title,
        department=department,
        experience_level=experience_level,
        key_skills=skills.split(',') if skills else None
    )
    
    return job_description


@router.post("/generate-questions", response_model=Dict[str, Any])
async def generate_interview_questions(
    job_title: str = Form(...),
    candidate_experience: Optional[str] = Form("mid"),
    focus_areas: Optional[str] = Form(None),
    question_count: int = Form(10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate interview questions using AI.
    """
    ai_service = AIService()
    
    questions = await ai_service.generate_interview_questions(
        job_context={"title": job_title, "experience_level": candidate_experience},
        count=question_count
    )
    
    return {
        "job_title": job_title,
        "questions": questions,
        "count": len(questions)
    }
