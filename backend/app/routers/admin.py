"""
Admin router for super admin functionality.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User, Organization
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.application import Application
from app.middleware.auth import get_super_admin_user
from app.schemas.user import UserResponse
from app.schemas.organization import OrganizationResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_super_admin_user),
) -> List[User]:
    """
    Get all users across all organizations (super admin only).
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_all_organizations(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_super_admin_user),
) -> List[Organization]:
    """
    Get all organizations (super admin only).
    """
    result = await db.execute(select(Organization))
    organizations = result.scalars().all()
    return organizations


@router.patch("/users/{user_id}")
async def update_user_admin_fields(
    user_id: str,
    is_active: bool = None,
    is_super_admin: bool = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_super_admin_user),
) -> Dict[str, Any]:
    """
    Update user's active status and super admin status (super admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent super admin from deactivating themselves
    if user_id == _.id and is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    # Prevent super admin from removing their own super admin status
    if user_id == _.id and is_super_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own super admin status",
        )

    if is_active is not None:
        user.is_active = is_active
    if is_super_admin is not None:
        user.is_super_admin = is_super_admin

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_super_admin": user.is_super_admin,
        "message": "User updated successfully"
    }


@router.get("/stats")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_super_admin_user),
) -> Dict[str, int]:
    """
    Get platform-wide statistics (super admin only).
    """
    # Count users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()

    # Count organizations
    result = await db.execute(select(func.count(Organization.id)))
    total_organizations = result.scalar()

    # Count jobs
    result = await db.execute(select(func.count(Job.id)))
    total_jobs = result.scalar()

    # Count candidates
    result = await db.execute(select(func.count(Candidate.id)))
    total_candidates = result.scalar()

    # Count applications
    result = await db.execute(select(func.count(Application.id)))
    total_applications = result.scalar()

    return {
        "total_users": total_users,
        "total_organizations": total_organizations,
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "total_applications": total_applications,
    }