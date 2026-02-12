from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.candidate import Candidate
from ..models.application import Application
from ..models.user import User, OrganizationMember
from ..schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateApplicationSummary,
    CandidateSearchRequest,
    CandidateImportItem,
    CandidateImportResponse,
    ResumeUploadResponse,
)
from ..services.parser_service import ParserService
from .auth import get_current_user

router = APIRouter(prefix="/candidates", tags=["candidates"])


async def _get_user_org_id(current_user: User, db: AsyncSession) -> str:
    """
    Helper to get the active organization ID for the current user.
    """
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    )
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any active organization",
        )
    return str(org_member.organization_id)


async def _get_candidate_for_org(
    candidate_id: UUID,
    org_id: str,
    db: AsyncSession,
) -> Candidate:
    """
    Fetch a candidate by ID scoped to the given organization.
    """
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == str(candidate_id),
            Candidate.organization_id == org_id,
        )
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    return candidate


@router.post(
    "/",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new candidate for the current user's organization.
    """
    org_id = await _get_user_org_id(current_user, db)

    candidate = Candidate(
        organization_id=org_id,
        email=candidate_data.email,
        first_name=candidate_data.first_name,
        last_name=candidate_data.last_name,
        phone=candidate_data.phone,
        location=candidate_data.location,
        timezone=candidate_data.timezone,
        headline=candidate_data.headline,
        summary=candidate_data.summary,
        avatar_url=candidate_data.avatar_url,
        resume_url=candidate_data.resume_url,
        portfolio_url=candidate_data.portfolio_url,
        linkedin_url=candidate_data.linkedin_url,
        github_url=candidate_data.github_url,
        twitter_url=candidate_data.twitter_url,
        website_url=candidate_data.website_url,
        total_experience_years=candidate_data.total_experience_years,
        desired_salary_min=candidate_data.desired_salary_min,
        desired_salary_max=candidate_data.desired_salary_max,
        desired_locations=candidate_data.desired_locations,
        open_to_remote=candidate_data.open_to_remote,
        tags=candidate_data.tags,
        source_id=candidate_data.source_id,
        source_details=candidate_data.source_details,
    )

    db.add(candidate)
    await db.flush()
    await db.refresh(candidate)

    return candidate


@router.get(
    "/",
    response_model=List[CandidateResponse],
)
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List candidates for the current user's organization with optional search.
    """
    org_id = await _get_user_org_id(current_user, db)

    stmt = select(Candidate).where(Candidate.organization_id == org_id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Candidate.first_name.ilike(pattern),
                Candidate.last_name.ilike(pattern),
                Candidate.email.ilike(pattern),
                Candidate.headline.ilike(pattern),
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    return candidates


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
async def get_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific candidate by ID for the current user's organization.
    """
    org_id = await _get_user_org_id(current_user, db)
    candidate = await _get_candidate_for_org(candidate_id, org_id, db)
    return candidate


@router.patch(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
async def update_candidate(
    candidate_id: UUID,
    candidate_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update candidate information.
    """
    org_id = await _get_user_org_id(current_user, db)
    candidate = await _get_candidate_for_org(candidate_id, org_id, db)

    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.flush()
    await db.refresh(candidate)

    return candidate


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a candidate.
    """
    org_id = await _get_user_org_id(current_user, db)
    candidate = await _get_candidate_for_org(candidate_id, org_id, db)

    db.delete(candidate)

    # Commit handled by session dependency
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{candidate_id}/resume",
    response_model=ResumeUploadResponse,
)
async def upload_resume(
    candidate_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and parse resume for a candidate.

    This parses the file into text, extracts basic contact info,
    and stores the parsed data on the candidate record.
    """
    org_id = await _get_user_org_id(current_user, db)
    candidate = await _get_candidate_for_org(candidate_id, org_id, db)

    content = await file.read()
    text = ParserService.extract_text(content, file.filename)

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to extract text from resume file",
        )

    contact_info = ParserService.extract_contact_info(text)

    # Update candidate fields when missing
    if not candidate.email and contact_info.get("email"):
        candidate.email = contact_info["email"]
    if not candidate.phone and contact_info.get("phone"):
        candidate.phone = contact_info["phone"]
    if not candidate.linkedin_url and contact_info.get("linkedin"):
        candidate.linkedin_url = contact_info["linkedin"]
    if not candidate.github_url and contact_info.get("github"):
        candidate.github_url = contact_info["github"]

    # Store parsed resume data
    candidate.parsed_resume = {
        "raw_text": text,
        "contact_info": contact_info,
    }
    candidate.resume_url = candidate.resume_url or f"uploaded://{file.filename}"

    await db.flush()
    await db.refresh(candidate)

    return ResumeUploadResponse(
        message="Resume uploaded and parsed successfully",
        candidate=candidate,
        parsed_contact=contact_info,
    )


@router.get(
    "/{candidate_id}/applications",
    response_model=List[CandidateApplicationSummary],
)
async def get_candidate_applications(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all applications for a specific candidate.
    """
    org_id = await _get_user_org_id(current_user, db)
    candidate = await _get_candidate_for_org(candidate_id, org_id, db)

    stmt = select(Application).where(Application.candidate_id == candidate.id)
    result = await db.execute(stmt)
    applications = result.scalars().all()

    return applications


@router.post(
    "/search",
    response_model=List[CandidateResponse],
)
async def search_candidates(
    payload: CandidateSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Semantic-ish candidate search (basic filters for now).

    This implements text search on name/email/headline plus simple filters.
    Vector-based search can be added later using resume embeddings.
    """
    org_id = await _get_user_org_id(current_user, db)

    stmt = select(Candidate).where(Candidate.organization_id == org_id)

    if payload.search:
        pattern = f"%{payload.search}%"
        stmt = stmt.where(
            or_(
                Candidate.first_name.ilike(pattern),
                Candidate.last_name.ilike(pattern),
                Candidate.email.ilike(pattern),
                Candidate.headline.ilike(pattern),
            )
        )

    if payload.location:
        stmt = stmt.where(Candidate.location.ilike(f"%{payload.location}%"))

    if payload.open_to_remote is not None:
        stmt = stmt.where(Candidate.open_to_remote == payload.open_to_remote)

    if payload.min_experience_years is not None:
        stmt = stmt.where(
            Candidate.total_experience_years >= payload.min_experience_years
        )

    stmt = stmt.offset(payload.offset).limit(payload.limit)
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    return candidates


@router.post(
    "/import",
    response_model=CandidateImportResponse,
)
async def import_candidates(
    items: List[CandidateImportItem],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk import candidates for the current user's organization.

    Existing candidates (by email within the same org) are skipped.
    """
    org_id = await _get_user_org_id(current_user, db)

    created = 0
    skipped = 0

    for item in items:
        # Check for existing candidate by email within org
        result = await db.execute(
            select(Candidate).where(
                Candidate.organization_id == org_id,
                Candidate.email == item.email,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        candidate = Candidate(
            organization_id=org_id,
            email=item.email,
            first_name=item.first_name,
            last_name=item.last_name,
            phone=item.phone,
            location=item.location,
            timezone=item.timezone,
            headline=item.headline,
            summary=item.summary,
            avatar_url=item.avatar_url,
            resume_url=item.resume_url,
            portfolio_url=item.portfolio_url,
            linkedin_url=item.linkedin_url,
            github_url=item.github_url,
            twitter_url=item.twitter_url,
            website_url=item.website_url,
            total_experience_years=item.total_experience_years,
            desired_salary_min=item.desired_salary_min,
            desired_salary_max=item.desired_salary_max,
            desired_locations=item.desired_locations,
            open_to_remote=item.open_to_remote,
            tags=item.tags,
            source_id=item.source_id,
            source_details=item.source_details,
        )
        db.add(candidate)
        created += 1

    return CandidateImportResponse(created=created, skipped=skipped)


@router.post("/{candidate_id}/generate-summary")
async def generate_candidate_summary(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-generate candidate summary (placeholder for future AI integration).
    """
    org_id = await _get_user_org_id(current_user, db)
    await _get_candidate_for_org(candidate_id, org_id, db)

    return {"message": "AI candidate summary generation endpoint"}
