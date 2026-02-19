"""
Authentication middleware for JWT verification and role-based access control.
"""
from typing import Optional, List, Dict, Any
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, OrganizationMember
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentMembership:
    """Container for current user membership information."""
    
    def __init__(self, user: User, organization_id: Optional[str], role: Optional[str]):
        self.user = user
        self.organization_id = organization_id
        self.role = role


async def get_current_membership(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentMembership:
    """
    Get current authenticated user membership information.
    
    Returns:
        CurrentMembership with user, organization_id, and role
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Get user's organization membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
        .limit(1)
    )
    member = result.scalar_one_or_none()
    
    organization_id = member.organization_id if member else None
    role = member.role.value if member else None
    
    return CurrentMembership(user=user, organization_id=organization_id, role=role)


async def get_current_user(
    membership: CurrentMembership = Depends(get_current_membership),
) -> User:
    """
    Get current authenticated user (legacy compatibility).
    """
    return membership.user


async def get_super_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are a super admin.
    Raises 403 if user is not a super admin.
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user


class RoleChecker:
    """
    Dependency class for role-based access control.
    Usage: Depends(RoleChecker(["admin", "manager"]))
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, membership: CurrentMembership = Depends(get_current_membership)) -> CurrentMembership:
        if membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        return membership


def require_roles(allowed_roles: List[str]):
    """
    Decorator for requiring specific roles.
    Usage: @require_roles(["admin", "manager"])
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, membership: CurrentMembership = Depends(get_current_membership), **kwargs):
            if membership.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                )
            return await func(*args, membership=membership, **kwargs)
        return wrapper
    return decorator


class OrganizationChecker:
    """
    Dependency class for organization-based access control.
    Ensures user can only access resources from their organization.
    """
    
    async def __call__(
        self,
        organization_id: str,
        membership: CurrentMembership = Depends(get_current_membership),
    ) -> CurrentMembership:
        if str(membership.organization_id) != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization's resources",
            )
        return membership
