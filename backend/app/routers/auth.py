"""Authentication router for user registration, login, and password management."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.schemas.auth import (
    RegisterRequest,
    RefreshTokenRequest,
    RegisterResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    RefreshTokenResponse,
    LoginResponse,
)
from app.schemas.user import UserResponse
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with email validation.
    Creates a new user account and returns user data with access token.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Create/find organization.
    org_name = user_data.organization_name or f"{user_data.first_name}'s Organization"
    result = await db.execute(select(Organization).where(Organization.name == org_name))
    organization = result.scalar_one_or_none()
    if not organization:
        organization = Organization(name=org_name)
        db.add(organization)
        await db.flush()
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    db.add(user)
    await db.flush()  # Get the ID
    
    member = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role=UserRole.RECRUITER.value,
    )
    db.add(member)
    
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "org_id": str(organization.id) if organization else None})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        },
        organization={
            "id": str(organization.id),
            "name": organization.name,
        },
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access/refresh tokens.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Get user's default organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
        .limit(1)
    )
    member = result.scalar_one_or_none()
    org_id = str(member.organization_id) if member else None
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "org_id": org_id})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    user.last_login = datetime.utcnow().isoformat()
    await db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        },
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    try:
        payload = decode_token(token_data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        # Verify user still exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # Get user's organization
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
            .limit(1)
        )
        member = result.scalar_one_or_none()
        org_id = str(member.organization_id) if member else None
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id), "org_id": org_id})
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout user (client should discard tokens).
    """
    # In a real implementation, you might want to blacklist tokens
    # For now, just return success
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information.
    """
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if user:
        # In a real implementation, send email with reset token
        # For now, just return success to avoid email enumeration
        pass
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using token.
    """
    try:
        # Decode and validate token
        payload = decode_token(request.token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token",
            )
        
        # Find user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )
        
        # Update password
        user.hashed_password = get_password_hash(request.new_password)
        await db.commit()
        
        return {"message": "Password reset successfully"}
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
