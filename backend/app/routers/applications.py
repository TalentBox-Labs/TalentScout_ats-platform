from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from .. import models

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_application(
    # application_data: ApplicationCreate,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Create a new application (candidate applies to job)
    """
    return {"message": "Create application endpoint"}


@router.get("/")
async def list_applications(
    job_id: Optional[UUID] = None,
    candidate_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List applications with optional filters
    """
    query = db.query(models.Application)
    
    if job_id:
        query = query.filter(models.Application.job_id == job_id)
    if candidate_id:
        query = query.filter(models.Application.candidate_id == candidate_id)
    if status_filter:
        query = query.filter(models.Application.status == status_filter)
    
    applications = query.offset(skip).limit(limit).all()
    return {"applications": applications}


@router.get("/{application_id}")
async def get_application(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific application by ID
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: UUID,
    new_status: str,
    db: Session = Depends(get_db)
):
    """
    Update application status (move through pipeline stages)
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # TODO: Update status and log activity
    application.status = new_status
    db.commit()
    db.refresh(application)
    
    return application


@router.post("/{application_id}/screen")
async def screen_application(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """
    AI-powered screening of application
    """
    return {"message": "AI screening endpoint"}


@router.post("/{application_id}/score")
async def score_application(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Calculate and update application score
    """
    return {"message": "Application scoring endpoint"}


@router.post("/{application_id}/notes")
async def add_note(
    application_id: UUID,
    # note_data: NoteCreate,  # TODO: Import schema
    db: Session = Depends(get_db)
):
    """
    Add a note to the application
    """
    return {"message": "Add note endpoint"}


@router.delete("/{application_id}")
async def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an application
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
