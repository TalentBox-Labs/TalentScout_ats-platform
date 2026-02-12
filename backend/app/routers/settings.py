"""
Settings and configuration router.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("/automation", response_model=Dict[str, Any])
async def get_automation_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get automation settings for the organization.
    """
    # For now, return default settings
    # In a real implementation, you'd store these in the database
    return {
        "autoScreening": False,
        "autoEmailResponses": True,
        "autoScheduleInterviews": False,
        "emailTemplates": {
            "welcome": "Welcome to our hiring process! We're excited to review your application.",
            "rejection": "Thank you for your interest. Unfortunately, we won't be moving forward with your application at this time.",
            "interviewInvite": "Congratulations! We'd like to schedule an interview with you.",
        },
        "slackIntegration": False,
        "calendarIntegration": False,
        "webhookUrl": "",
    }


@router.put("/automation", response_model=Dict[str, Any])
async def update_automation_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update automation settings for the organization.
    """
    # For now, just return the settings
    # In a real implementation, you'd validate and store these in the database
    return settings