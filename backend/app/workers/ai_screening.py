"""
Celery worker for AI-powered candidate screening.
"""
from celery import Celery
from sqlalchemy import select
import asyncio

from app.config import settings
from app.database import async_session_maker
from app.models.application import Application, ApplicationActivity, ActivityType
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.ai_service import AIService

# Initialize Celery
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
    include=["app.workers.ai_screening", "app.workers.embedding_worker", "app.workers.resume_parser"],
)


@celery_app.task(name="screen_candidate_task")
def screen_candidate_task(application_id: str):
    """
    Run AI screening for a candidate application.
    """
    asyncio.run(_screen_candidate_async(application_id))


async def _screen_candidate_async(application_id: str):
    """
    Async function to screen candidate using AI.
    """
    async with async_session_maker() as db:
        # Fetch application with related data
        result = await db.execute(
            select(Application)
            .where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()
        
        if not application:
            raise ValueError(f"Application {application_id} not found")
        
        # Fetch candidate
        result = await db.execute(
            select(Candidate).where(Candidate.id == application.candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        # Fetch job
        result = await db.execute(
            select(Job).where(Job.id == application.job_id)
        )
        job = result.scalar_one_or_none()
        
        if not candidate or not job:
            raise ValueError(f"Candidate or Job not found for application {application_id}")
        
        # Prepare candidate data for screening
        candidate_data = {
            "name": f"{candidate.first_name} {candidate.last_name}",
            "email": candidate.email,
            "current_position": candidate.current_position,
            "current_company": candidate.current_company,
            "years_of_experience": candidate.years_of_experience,
            "location": candidate.location,
            "summary": candidate.summary,
            "resume_text": "",  # Should fetch from parsed resume
        }
        
        # Prepare job data
        job_data = {
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "skills_required": job.skills_required,
            "experience_level": job.experience_level,
            "location": job.location,
        }
        
        # Run AI screening
        ai_service = AIService()
        screening_result = await ai_service.screen_candidate(candidate_data, job_data)
        
        # Update application with AI insights
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
            activity_metadata=screening_result,
        )
        db.add(activity)
        
        await db.commit()
        
        print(f"AI screening completed for application {application_id}")
        print(f"Fit score: {screening_result.get('fit_score')}%")
