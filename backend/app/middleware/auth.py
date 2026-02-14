"""
Authentication middleware for JWT verification and role-based access control.
"""
from typing import List
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, OrganizationMember
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    token_org_id = payload.get("org_id")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == str(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    membership_query = select(OrganizationMember).where(
        OrganizationMember.user_id == user.id,
        OrganizationMember.is_active == True,
    )
    if token_org_id:
        membership_query = membership_query.where(
            OrganizationMember.organization_id == str(token_org_id)
        )
    membership_query = membership_query.limit(1)

    membership_result = await db.execute(membership_query)
    membership = membership_result.scalar_one_or_none()

    # Expose effective org/role for existing router code paths.
    user.organization_id = membership.organization_id if membership else None  # type: ignore[attr-defined]
    if membership:
        user.role = getattr(membership.role, "value", membership.role)  # type: ignore[attr-defined]
    else:
        user.role = None  # type: ignore[attr-defined]
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


class RoleChecker:
    """
    Dependency class for role-based access control.
    Usage: Depends(RoleChecker(["admin", "manager"]))
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        return current_user


def require_roles(allowed_roles: List[str]):
    """
    Decorator for requiring specific roles.
    Usage: @require_roles(["admin", "manager"])
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user.role or current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                )
            return await func(*args, current_user=current_user, **kwargs)
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
        current_user: User = Depends(get_current_user),
    ) -> User:
        if str(current_user.organization_id) != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization's resources",
            )
        return current_user
