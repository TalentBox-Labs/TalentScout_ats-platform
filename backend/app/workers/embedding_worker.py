"""
Celery worker for generating job embeddings using AI service.
"""
from celery import Celery
from sqlalchemy import select
import asyncio

from app.config import settings
from app.database import async_session_maker
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
)


@celery_app.task(name="generate_job_embedding")
def generate_job_embedding(job_id: str):
    """
    Generate embedding for a job posting using AI service.
    This task runs asynchronously in Celery worker.
    """
    asyncio.run(_generate_job_embedding_async(job_id))


async def _generate_job_embedding_async(job_id: str):
    """
    Async function to generate job embedding.
    """
    async with async_session_maker() as db:
        # Fetch job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Create text for embedding
        embedding_text = f"""
        Title: {job.title}
        Description: {job.description}
        Requirements: {job.requirements or ''}
        Responsibilities: {job.responsibilities or ''}
        Skills: {', '.join(job.skills_required)}
        Department: {job.department or ''}
        Experience Level: {job.experience_level}
        """
        
        # Generate embedding using AI service
        ai_service = AIService()
        embedding = await ai_service.generate_embedding(embedding_text)
        
        # Store embedding in database
        job.embedding = embedding
        await db.commit()
        
        print(f"Generated embedding for job {job_id}")
