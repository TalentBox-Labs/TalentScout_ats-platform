"""
Onboarding and setup router.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_membership, CurrentMembership

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/status", response_model=Dict[str, Any])
async def get_onboarding_status(
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Get onboarding completion status.
    """
    # For now, return default status
    # In a real implementation, you'd track this in the database
    return {
        "currentStep": 0,
        "steps": [
            {
                "id": "company",
                "title": "Company Information",
                "description": "Set up your company profile",
                "completed": False,
                "required": True,
            },
            {
                "id": "email",
                "title": "Email Integration",
                "description": "Connect your email service",
                "completed": False,
                "required": True,
            },
            {
                "id": "jobs",
                "title": "Create First Job",
                "description": "Post your first job opening",
                "completed": False,
                "required": True,
            },
            {
                "id": "team",
                "title": "Invite Team Members",
                "description": "Add colleagues to your team",
                "completed": False,
                "required": False,
            },
            {
                "id": "settings",
                "title": "Configure Settings",
                "description": "Set up automation and preferences",
                "completed": False,
                "required": False,
            },
        ],
    }


@router.post("/complete/{step_id}", response_model=Dict[str, Any])
async def complete_onboarding_step(
    step_id: str,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark an onboarding step as completed.
    """
    # For now, just return success
    # In a real implementation, you'd update the database
    return {
        "step_id": step_id,
        "completed": True,
        "message": f"Step {step_id} completed successfully",
    }