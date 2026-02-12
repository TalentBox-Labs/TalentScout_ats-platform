"""
Celery worker for parsing resumes and generating embeddings.
"""
from celery import Celery
from sqlalchemy import select
import asyncio

from app.config import settings
from app.database import async_session_maker
from app.models.candidate import Candidate, CandidateExperience, CandidateEducation, CandidateSkill
from app.services.parser_service import ParserService
from app.services.ai_service import AIService

# Initialize Celery (reuse from embedding_worker or create shared config)
celery_app = Celery(
    "workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="parse_resume_task")
def parse_resume_task(candidate_id: str, resume_url: str, content_type: str):
    """
    Parse resume and extract structured data.
    """
    asyncio.run(_parse_resume_async(candidate_id, resume_url, content_type))


async def _parse_resume_async(candidate_id: str, resume_url: str, content_type: str):
    """
    Async function to parse resume.
    """
    async with async_session_maker() as db:
        # Fetch candidate
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Download resume bytes
        # For now, assume resume_url is a local file path
        try:
            with open(resume_url, 'rb') as f:
                file_bytes = f.read()
        except Exception as e:
            raise ValueError(f"Failed to download/read resume file: {str(e)}")
        
        # Determine filename from URL/path
        filename = resume_url.split('/')[-1] or f"resume.{content_type.split('/')[-1]}"
        
        # Parse resume file using synchronous parser
        parser_service = ParserService()
        resume_text = parser_service.extract_text(file_bytes, filename)
        
        if not resume_text:
            raise ValueError("Failed to extract text from resume")
        
        # Use AI to parse resume and extract structured data
        ai_service = AIService()
        parsed_data = await ai_service.parse_resume_text(resume_text)
        
        # Update candidate with parsed data
        if parsed_data.get("summary"):
            candidate.summary = parsed_data["summary"]
        if parsed_data.get("current_position"):
            candidate.current_position = parsed_data["current_position"]
        if parsed_data.get("current_company"):
            candidate.current_company = parsed_data["current_company"]
        if parsed_data.get("years_of_experience"):
            candidate.years_of_experience = parsed_data["years_of_experience"]
        if parsed_data.get("location"):
            candidate.location = parsed_data["location"]
        if parsed_data.get("phone"):
            candidate.phone = parsed_data["phone"]
        
        # Add experience entries
        for exp in parsed_data.get("experience", []):
            experience = CandidateExperience(
                candidate_id=candidate.id,
                company=exp["company"],
                title=exp["position"],
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                is_current=exp.get("is_current", False),
                description=exp.get("description"),
            )
            db.add(experience)
        
        # Add education entries
        for edu in parsed_data.get("education", []):
            education = CandidateEducation(
                candidate_id=candidate.id,
                institution=edu["institution"],
                degree=edu["degree"],
                field_of_study=edu.get("field_of_study"),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
            )
            db.add(education)
        
        # Add skills
        for skill_name in parsed_data.get("skills", []):
            skill = CandidateSkill(
                candidate_id=candidate.id,
                name=skill_name,
            )
            db.add(skill)
        
        # Generate embedding from resume text
        embedding = await ai_service.generate_embedding(resume_text)
        candidate.resume_embedding = embedding
        
        await db.commit()
        
        print(f"Successfully parsed resume for candidate {candidate_id}")
