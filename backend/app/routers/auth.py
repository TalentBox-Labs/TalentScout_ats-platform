<<<<<<< HEAD
"""
Authentication router for user registration, login, and password management.
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
    ForgotPassword,
    ResetPassword,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with email validation.
    Creates a new user account and returns user data with access token.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
=======
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..database import get_db
from ..schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from ..schemas.user import UserResponse
from ..utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token,
)
from ..models.user import User, Organization, OrganizationMember, UserRole
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and create default organization
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == payload.email))
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
<<<<<<< HEAD
            detail="Email already registered",
        )
    
    # Create organization if it doesn't exist
    from app.models.organization import Organization
    result = await db.execute(select(Organization).where(Organization.name == user_data.organization_name))
    organization = result.scalar_one_or_none()
    
    if not organization:
        organization = Organization(name=user_data.organization_name)
        db.add(organization)
        await db.commit()
        await db.refresh(organization)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        organization_id=organization.id,
        role="recruiter",
        is_active=True,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.email, "user_id": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": new_user.email, "user_id": str(new_user.id)})
    
    return {
        "user": new_user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password to get JWT tokens.
    Returns access token and refresh token.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
=======
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(payload.password)
    db_user = User(
        email=payload.email,
        hashed_password=hashed_password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_verified=False
    )
    db.add(db_user)
    await db.flush()  # Get user ID
    
    # Create default organization
    org_name = payload.organization_name or f"{payload.first_name}'s Organization"
    organization = Organization(
        name=org_name,
        domain=payload.email.split('@')[1],
        is_active=True
    )
    db.add(organization)
    await db.flush()
    
    # Link user to organization
    org_member = OrganizationMember(
        organization_id=organization.id,
        user_id=db_user.id,
        role=UserRole.ADMIN if payload.role == "admin" else UserRole.RECRUITER,
        is_active=True
    )
    db.add(org_member)
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": str(db_user.id), "org_id": str(organization.id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": db_user.email, "user_id": str(db_user.id)}
    )
    
    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": str(db_user.id),
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "full_name": db_user.full_name
        },
        organization={
            "id": str(organization.id),
            "name": organization.name
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_data: Optional[LoginRequest] = Body(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token
    """
    # Support both OAuth2PasswordRequestForm (Swagger) and JSON body (frontend client)
    if login_data:
        email = login_data.email
        password = login_data.password
    else:
        email = form_data.username
        password = form_data.password

    # Authenticate user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
<<<<<<< HEAD
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Generate tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "organization_id": str(user.organization_id)}
=======
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Get user's organizations
    org_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
    )
    org_member = org_result.scalar_one_or_none()
    
    org_id = str(org_member.organization_id) if org_member else None
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "org_id": org_id}
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
<<<<<<< HEAD
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    try:
        payload = decode_token(token_data.refresh_token)
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
=======

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal)
    """
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using a valid refresh token.
    """
    token_data = decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
<<<<<<< HEAD
    
    # Generate new tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "organization_id": str(user.organization_id)}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user (client should discard tokens).
    In production, implement token blacklisting with Redis.
    """
    # TODO: Implement token blacklisting in Redis
    # await redis.setex(f"blacklist:{token}", settings.access_token_expire_minutes * 60, "1")
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's profile.
    """
    return {
        "user": current_user,
        "access_token": None,
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset email.
    Sends a password reset link to the user's email.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate password reset token (valid for 1 hour)
    reset_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1),
    )
    
    # TODO: Send email with reset link
    # await send_password_reset_email(user.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using reset token from email.
    """
    try:
        payload = decode_token(data.token)
        email = payload.get("sub")
        user_id = payload.get("user_id")
        token_type = payload.get("type")
        
        if email is None or user_id is None or token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )
    except Exception:
=======

    # Get user's active organization (if any)
    org_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    )
    org_member = org_result.scalar_one_or_none()
    org_id = str(org_member.organization_id) if org_member else None

    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "org_id": org_id}
    )

    return RefreshTokenResponse(access_token=access_token, token_type="bearer")


@router.post("/forgot-password")
async def forgot_password(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate password reset for a user.

    In production, this would send an email with a reset link.
    In development, we also return the token in the response for convenience.
    """
    # Look up user by email (but don't reveal whether they exist)
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        # Always respond with success to avoid account enumeration
        return {"message": "If an account exists for this email, a reset link has been sent."}

    reset_token = create_password_reset_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )

    response: dict = {
        "message": "If an account exists for this email, a reset link has been sent."
    }

    # Expose token in non-production environments for easier testing
    if settings.environment != "production":
        response["reset_token"] = reset_token

    return response


@router.post("/reset-password")
async def reset_password(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm password reset using a valid reset token.
    """
    token_data = decode_token(payload.token)
    if not token_data or token_data.get("type") != "password_reset":
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
<<<<<<< HEAD
    
    # Find user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    
    return {"message": "Password has been reset successfully"}
=======

    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )

    # Update password
    user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()

    return {"message": "Password has been reset successfully."}
>>>>>>> 5d2116f11babd3814a39d8d56d48d2e1785992f5
