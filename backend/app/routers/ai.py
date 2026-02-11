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
