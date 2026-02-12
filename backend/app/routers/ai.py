<<<<<<< HEAD
"""
AI services router for resume parsing, screening, and generation tasks.
"""
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, and_

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationActivity, ActivityType
from app.models.candidate import Candidate
from app.models.job import Job
from app.middleware.auth import get_current_user
from app.schemas.ai import (
    ResumeParseRequest,
    ResumeParseResponse,
    CandidateMatchRequest,
    CandidateMatchResponse,
    EmailGenerationRequest,
    EmailGenerationResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    JobDescriptionRequest,
    JobDescriptionResponse,
)
from app.services.ai_service import AIService
from app.services.parser_service import ParserService

router = APIRouter(prefix="/api/v1/ai", tags=["ai-services"])


@router.post("/parse-resume", response_model=ResumeParseResponse)
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Parse resume file and extract structured data.
    """
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOCX, and TXT are allowed",
        )
    
    # Read file content
    file_content = await file.read()
    
    # Extract text
    parser_service = ParserService()
    resume_text = await parser_service.extract_text_from_bytes(file_content, file.content_type)
    
    # Parse with AI
    ai_service = AIService()
    parsed_data = await ai_service.parse_resume_text(resume_text)
    
    return {
        "success": True,
        "data": parsed_data,
        "message": "Resume parsed successfully",
    }


@router.post("/screen/{application_id}", response_model=Dict[str, Any])
async def re_run_ai_screening(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Re-run AI screening for an application.
    """
    # Fetch application with related data
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
    
    # Fetch candidate and job
    candidate_result = await db.execute(select(Candidate).where(Candidate.id == application.candidate_id))
    candidate = candidate_result.scalar_one_or_none()
    
    job_result = await db.execute(select(Job).where(Job.id == application.job_id))
    job = job_result.scalar_one_or_none()
    
    if not candidate or not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate or Job not found",
        )
    
    # Prepare data
    candidate_data = {
        "name": f"{candidate.first_name} {candidate.last_name}",
        "email": candidate.email,
        "current_position": candidate.current_position,
        "current_company": candidate.current_company,
        "years_of_experience": candidate.years_of_experience,
        "location": candidate.location,
        "summary": candidate.summary,
    }
    
    job_data = {
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements,
        "responsibilities": job.responsibilities,
        "skills_required": job.skills_required,
        "experience_level": job.experience_level,
    }
    
    # Run screening
    ai_service = AIService()
    screening_result = await ai_service.screen_candidate(candidate_data, job_data)
    
    # Update application
    application.ai_match_score = screening_result.get("fit_score")
    application.ai_insights = screening_result.get("summary")
    application.ai_strengths = screening_result.get("strengths", [])
    application.ai_concerns = screening_result.get("concerns", [])
    application.ai_recommendation = screening_result.get("recommendation")
    
    # Create activity log
    activity = ApplicationActivity(
        application_id=application.id,
        activity_type=ActivityType.SCREENING_COMPLETED,
        title="AI Screening Completed",
        description=f"AI screening completed with fit score: {screening_result.get('fit_score')}%",
        metadata=screening_result,
    )
    db.add(activity)
    
    await db.commit()
    
    return screening_result


@router.post("/match-candidates", response_model=CandidateMatchResponse)
async def match_candidates_to_job(
    match_request: CandidateMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Find matching candidates for a job using semantic search.
    """
    # Fetch job
    result = await db.execute(
        select(Job).where(
            and_(
                Job.id == match_request.job_id,
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
    
    # Use job embedding to find similar candidates
    if not job.embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job embedding not generated yet. Please wait.",
        )
    
    # Perform vector similarity search with parameterized query
    query = text("""
        SELECT
            id,
            first_name,
            last_name,
            email,
            headline as current_position,
            current_company,
            location,
            total_experience_years as years_of_experience,
            1 - (resume_embedding <=> :job_embedding::vector) as similarity_score
        FROM candidates
        WHERE organization_id = :org_id
            AND resume_embedding IS NOT NULL
        ORDER BY resume_embedding <=> :job_embedding::vector
        LIMIT :limit_val
    """)

    result = await db.execute(query, {
        "job_embedding": job.embedding,
        "org_id": str(current_user.organization_id),
        "limit_val": match_request.limit or 20
    })
    candidates = result.fetchall()
    
    # Format results
    matches = []
    for row in candidates:
        if row.similarity_score >= (match_request.min_score or 0.6):
            matches.append({
                "candidate_id": str(row.id),
                "first_name": row.first_name,
                "last_name": row.last_name,
                "email": row.email,
                "current_position": row.current_position,
                "current_company": row.current_company,
                "location": row.location,
                "years_of_experience": row.years_of_experience,
                "match_score": float(row.similarity_score),
                "explanation": f"Match score: {row.similarity_score:.2%}",
            })
    
    return {
        "job_id": str(match_request.job_id),
        "total_matches": len(matches),
        "matches": matches,
    }


@router.post("/generate-email", response_model=EmailGenerationResponse)
async def generate_email(
    email_request: EmailGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate email content using AI.
    """
    ai_service = AIService()
    
    # Generate email based on template type
    email_content = await ai_service.generate_email(
        context=email_request.context,
        email_type=email_request.template_type,
        tone=email_request.tone,
    )
    
    return {
        "subject": email_content.get("subject"),
        "body": email_content.get("body"),
        "template_type": email_request.template_type,
    }


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_interview_questions(
    question_request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate interview questions for a job.
    """
    # Fetch job if job_id provided
    job_context = question_request.job_context
    if question_request.job_id:
        result = await db.execute(
            select(Job).where(
                and_(
                    Job.id == question_request.job_id,
                    Job.organization_id == current_user.organization_id
                )
            )
        )
        job = result.scalar_one_or_none()
        
        if job:
            job_context = {
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "experience_level": job.experience_level,
            }
    
    ai_service = AIService()
    questions = await ai_service.generate_interview_questions(
        job_context=job_context,
        question_types=question_request.question_types,
        count=question_request.count,
    )
    
    return {
        "questions": questions,
        "total": len(questions),
    }


@router.post("/generate-job-description", response_model=JobDescriptionResponse)
async def generate_job_description(
    job_request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate or enhance job description using AI.
    """
    ai_service = AIService()
    
    job_description = await ai_service.generate_job_description(
        title=job_request.title,
        department=job_request.department,
        experience_level=job_request.experience_level,
        key_skills=job_request.key_skills,
        additional_context=job_request.additional_context,
    )
    
    return {
        "title": job_description.get("title"),
        "description": job_description.get("description"),
        "requirements": job_description.get("requirements"),
        "responsibilities": job_description.get("responsibilities"),
        "suggested_skills": job_description.get("suggested_skills", []),
    }
=======
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..services.ai_service import AIService
from ..services.parser_service import ParserService
from ..services.matching_service import MatchingService

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize services
ai_service = AIService()
parser_service = ParserService()
matching_service = MatchingService()


@router.post("/parse-resume")
async def parse_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Parse resume using AI and extract structured data
    """
    try:
        # Read file
        content = await file.read()
        
        # Parse resume
        parsed_data = await parser_service.parse_resume(content, file.filename)
        
        return {
            "status": "success",
            "data": parsed_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )


@router.post("/match-candidates/{job_id}")
async def match_candidates(
    job_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Find best matching candidates for a job using AI
    """
    try:
        matches = await matching_service.find_matches(job_id, limit, db)
        return {
            "status": "success",
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match candidates: {str(e)}"
        )


@router.post("/screen-candidate/{application_id}")
async def screen_candidate(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """
    AI-powered screening of candidate for specific application
    """
    try:
        screening_result = await ai_service.screen_candidate(application_id, db)
        return {
            "status": "success",
            "screening": screening_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to screen candidate: {str(e)}"
        )


@router.post("/generate-job-description")
async def generate_job_description(
    # job_brief: JobBrief,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Generate job description using AI from brief
    """
    try:
        # job_description = await ai_service.generate_job_description(job_brief)
        return {
            "status": "success",
            "message": "AI job description generation"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate job description: {str(e)}"
        )


@router.post("/generate-email")
async def generate_email(
    # email_context: EmailContext,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Generate personalized email using AI
    """
    try:
        # email_content = await ai_service.generate_email(email_context)
        return {
            "status": "success",
            "message": "AI email generation"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email: {str(e)}"
        )


@router.post("/generate-screening-questions/{job_id}")
async def generate_screening_questions(
    job_id: UUID,
    num_questions: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered screening questions for a job
    """
    try:
        # questions = await ai_service.generate_screening_questions(job_id, num_questions, db)
        return {
            "status": "success",
            "message": "AI screening questions generation"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate screening questions: {str(e)}"
        )


@router.post("/analyze-interview-feedback/{interview_id}")
async def analyze_interview_feedback(
    interview_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Analyze interview feedback using AI for sentiment and insights
    """
    try:
        # analysis = await ai_service.analyze_interview_feedback(interview_id, db)
        return {
            "status": "success",
            "message": "AI interview feedback analysis"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze feedback: {str(e)}"
        )
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
