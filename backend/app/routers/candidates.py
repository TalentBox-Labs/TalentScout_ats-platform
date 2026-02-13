"""
Candidate management router with resume parsing and semantic search.
"""
from typing import List, Optional
from uuid import UUID
import io

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate, CandidateExperience, CandidateEducation, CandidateSkill
from app.middleware.auth import get_current_user
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    CandidateSearchRequest,
    CandidateSearchResponse,
    ExperienceResponse,
    EducationResponse,
)
from app.config import Settings
from app.workers.resume_parser import parse_resume_task
from app.services.ai_service import AIService

# Get settings
settings = Settings()

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=List[CandidateListResponse])
async def list_candidates(
    search: Optional[str] = Query(None, description="Search by name or email"),
    location: Optional[str] = Query(None, description="Filter by location"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all candidates with pagination and filters.
    """
    query = select(Candidate).where(Candidate.organization_id == current_user.organization_id)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Candidate.first_name.ilike(search_filter),
                Candidate.last_name.ilike(search_filter),
                Candidate.email.ilike(search_filter)
            )
        )
    if location:
        query = query.where(Candidate.location.ilike(f"%{location}%"))
    
    # Order by created date descending
    query = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    return candidates


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a candidate manually.
    """
    # Check if candidate with same email exists
    result = await db.execute(
        select(Candidate).where(
            and_(
                Candidate.email == candidate_data.email,
                Candidate.organization_id == current_user.organization_id
            )
        )
    )
    existing_candidate = result.scalar_one_or_none()
    
    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate with this email already exists",
        )
    
    new_candidate = Candidate(
        first_name=candidate_data.first_name,
        last_name=candidate_data.last_name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        location=candidate_data.location,
        linkedin_url=candidate_data.linkedin_url,
        github_url=candidate_data.github_url,
        portfolio_url=candidate_data.portfolio_url,
        current_position=candidate_data.current_position,
        current_company=candidate_data.current_company,
        years_of_experience=candidate_data.years_of_experience,
        organization_id=current_user.organization_id,
        source=candidate_data.source or "manual",
    )
    
    db.add(new_candidate)
    await db.commit()
    await db.refresh(new_candidate)
    
    return new_candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get candidate profile with experience, education, and skills.
    """
    result = await db.execute(
        select(Candidate)
        .where(and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == current_user.organization_id
        ))
        .options(
            selectinload(Candidate.experiences),
            selectinload(Candidate.education),
            selectinload(Candidate.skills)
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    return candidate


@router.patch("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: UUID,
    candidate_data: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update candidate details.
    """
    result = await db.execute(
        select(Candidate).where(and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == current_user.organization_id
        ))
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Update fields
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    await db.commit()
    await db.refresh(candidate)
    
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a candidate.
    """
    result = await db.execute(
        select(Candidate).where(and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == current_user.organization_id
        ))
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Soft delete - just mark as inactive or delete
    await db.delete(candidate)
    await db.commit()
    
    return None


@router.post("/{candidate_id}/resume", response_model=dict)
async def upload_resume(
    candidate_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload resume for a candidate (PDF/DOCX/TXT).
    Triggers background parsing and embedding generation.
    """
    result = await db.execute(
        select(Candidate).where(and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == current_user.organization_id
        ))
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOCX, and TXT are allowed",
        )
    
    # Read file content
    file_content = await file.read()
    
    # Upload to S3
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        
        # Generate unique filename
        import uuid
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        s3_key = f"candidates/{candidate_id}/resumes/{unique_filename}"
        
        # Upload file to S3
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type,
            ACL='private'  # Files are private, accessed via signed URLs
        )
        
        # Generate S3 URL
        s3_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
        candidate.resume_url = s3_url
        
    except NoCredentialsError:
        # Fallback to local storage if S3 credentials not configured
        import os
        upload_dir = f"uploads/{candidate_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = f"{upload_dir}/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        candidate.resume_url = file_path
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to S3: {str(e)}",
        )
    
    await db.commit()
    
    # Queue resume parsing in background
    parse_resume_task.delay(str(candidate_id), candidate.resume_url, file.content_type)
    
    return {
        "message": "Resume uploaded successfully. Parsing in progress.",
        "candidate_id": str(candidate_id),
        "filename": file.filename,
    }


@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def bulk_import_candidates(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk import candidates from CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed",
        )
    
    # TODO: Implement CSV parsing and bulk insert
    # This is a placeholder for the actual implementation
    
    return {
        "message": "Bulk import started. You will be notified when it completes.",
        "status": "processing",
    }


@router.post("/search", response_model=CandidateSearchResponse)
async def semantic_search_candidates(
    search_request: CandidateSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Semantic search for candidates using vector similarity.
    """
    ai_service = AIService()
    
    # Generate embedding for search query
    query_embedding = await ai_service.generate_embedding(search_request.query)
    
    # Perform vector similarity search using pgvector with parameterized query
    # This uses the <=> operator for cosine distance
    query = text("""
        SELECT 
            id,
            first_name,
            last_name,
            email,
            current_position,
            current_company,
            location,
            resume_url,
            1 - (resume_embedding <=> :query_embedding) as similarity_score
        FROM candidates
        WHERE organization_id = :org_id
            AND resume_embedding IS NOT NULL
        ORDER BY resume_embedding <=> :query_embedding
        LIMIT :limit_val
    """)
    
    result = await db.execute(query, {
        "query_embedding": query_embedding,
        "org_id": str(current_user.organization_id),
        "limit_val": search_request.limit or 20
    })
    candidates = result.fetchall()
    
    # Format results
    results = []
    for row in candidates:
        if row.similarity_score >= (search_request.min_score or 0.5):
            results.append({
                "candidate_id": str(row.id),
                "first_name": row.first_name,
                "last_name": row.last_name,
                "email": row.email,
                "current_position": row.current_position,
                "current_company": row.current_company,
                "location": row.location,
                "similarity_score": float(row.similarity_score),
                "match_explanation": f"Match score: {row.similarity_score:.2%}",
            })
    
    return {
        "query": search_request.query,
        "total_results": len(results),
        "results": results,
    }