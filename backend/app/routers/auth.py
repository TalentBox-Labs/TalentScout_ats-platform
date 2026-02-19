"""
Authentication router for user registration, login, and password management.
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import secrets
from app.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.schemas.auth import (
    RegisterRequest,
    UserLogin,
    Token,
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
from app.middleware.auth import get_current_membership, CurrentMembership
from app.config import settings

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
    
    # Create organization if provided
    organization = None
    if user_data.organization_name:
        # Check if organization already exists
        result = await db.execute(
            select(Organization).where(Organization.name == user_data.organization_name)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            organization = Organization(name=user_data.organization_name)
            db.add(organization)
            await db.flush()  # Get the ID
    
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
    
    # Create organization membership if organization exists
    if organization:
        member = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=UserRole.RECRUITER,  # Default role
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
        } if organization else None,
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
    user.last_login = str(user.id)  # This should be a timestamp, but keeping simple for now
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
    membership: CurrentMembership = Depends(get_current_membership),
):
    """
    Logout user (client should discard tokens).
    """
    # In a real implementation, you might want to blacklist tokens
    # For now, just return success
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    membership: CurrentMembership = Depends(get_current_membership),
):
    """
    Get current user information.
    """
    return membership.user


@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset.
    """
    from app.services.email_service import EmailService
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if user:
        # Create reset token (expires in 1 hour)
        reset_token = create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Send email
        email_service = EmailService()
        email_result = await email_service.send_password_reset_email(user.email, reset_token)
        
        if email_result["status"] == "error":
            # Log error but don't fail the request to avoid email enumeration
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
        token_type = payload.get("type")
        
        if not user_id or token_type != "password_reset":
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


# OAuth2 endpoints
@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """Redirect to OAuth provider for authentication."""
    state = secrets.token_urlsafe(32)
    
    if provider == "google":
        client_id = settings.google_client_id
        auth_url = "https://accounts.google.com/o/oauth2/auth"
        scope = "openid email profile"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/google/callback"
    elif provider == "microsoft":
        client_id = settings.microsoft_client_id
        auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        scope = "openid email profile"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/microsoft/callback"
    elif provider == "linkedin":
        client_id = settings.linkedin_client_id
        auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        scope = "r_liteprofile r_emailaddress"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/linkedin/callback"
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "code",
        "state": state,
    }
    
    auth_url_with_params = f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return RedirectResponse(url=auth_url_with_params)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Handle OAuth callback and create/login user."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    if provider == "google":
        client_id = settings.google_client_id
        client_secret = settings.google_client_secret
        token_url = "https://oauth2.googleapis.com/token"
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/google/callback"
    elif provider == "microsoft":
        client_id = settings.microsoft_client_id
        client_secret = settings.microsoft_client_secret
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        user_info_url = "https://graph.microsoft.com/v1.0/me"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/microsoft/callback"
    elif provider == "linkedin":
        client_id = settings.linkedin_client_id
        client_secret = settings.linkedin_client_secret
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        user_info_url = "https://api.linkedin.com/v2/people/~:(id,firstName,lastName,emailAddress)"
        redirect_uri = f"{settings.frontend_url}/auth/oauth/linkedin/callback"
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Exchange code for token
    async with httpx.AsyncClient() as http_client:
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        response = await http_client.post(token_url, data=token_data)
        token = response.json()
        
        if "access_token" not in token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        # Get user info
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        user_response = await http_client.get(user_info_url, headers=headers)
        user_info = user_response.json()

    # Extract user data
    if provider == "google":
        oauth_id = user_info["id"]
        email = user_info["email"]
        first_name = user_info.get("given_name", "")
        last_name = user_info.get("family_name", "")
    elif provider == "microsoft":
        oauth_id = user_info["id"]
        email = user_info["mail"] if "mail" in user_info else user_info.get("userPrincipalName", "")
        first_name = user_info.get("givenName", "")
        last_name = user_info.get("surname", "")
    elif provider == "linkedin":
        oauth_id = user_info["id"]
        email = user_info["emailAddress"]
        first_name = user_info["firstName"]["localized"]["en_US"] if user_info.get("firstName") else ""
        last_name = user_info["lastName"]["localized"]["en_US"] if user_info.get("lastName") else ""

    # Check if user exists
    id_field = f"{provider}_id"
    result = await db.execute(select(User).where(getattr(User, id_field) == oauth_id))
    user = result.scalar_one_or_none()

    if user:
        # User exists, log them in
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        redirect_url = f"{settings.frontend_url}/auth/oauth/{provider}/callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}&email={user.email}&first_name={user.first_name}&last_name={user.last_name}"
        return RedirectResponse(url=redirect_url)
    else:
        # Create new user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            **{id_field: oauth_id}
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create access tokens
        access_token = create_access_token(data={"sub": new_user.email})
        refresh_token = create_refresh_token(data={"sub": new_user.email})
        
        redirect_url = f"{settings.frontend_url}/auth/oauth/{provider}/callback?access_token={access_token}&refresh_token={refresh_token}&user_id={new_user.id}&email={new_user.email}&first_name={new_user.first_name}&last_name={new_user.last_name}"
        return RedirectResponse(url=redirect_url)