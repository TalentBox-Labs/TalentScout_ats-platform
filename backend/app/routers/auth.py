"""Authentication router for user registration, login, and password management."""
from datetime import datetime
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

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
from app.config import settings

# In-memory store for OAuth states (in production, use Redis/database)
oauth_states = {}

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 configurations
GOOGLE_OAUTH_CONFIG = {
    'client_id': settings.google_client_id,
    'client_secret': settings.google_client_secret,
    'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
    'access_token_url': 'https://oauth2.googleapis.com/token',
    'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
    'scope': 'openid email profile',
}

MICROSOFT_OAUTH_CONFIG = {
    'client_id': settings.microsoft_client_id,
    'client_secret': settings.microsoft_client_secret,
    'authorize_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    'access_token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    'userinfo_url': 'https://graph.microsoft.com/v1.0/me',
    'scope': 'openid email profile',
}

LINKEDIN_OAUTH_CONFIG = {
    'client_id': settings.linkedin_client_id,
    'client_secret': settings.linkedin_client_secret,
    'authorize_url': 'https://www.linkedin.com/oauth/v2/authorization',
    'access_token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
    'userinfo_url': 'https://api.linkedin.com/v2/people/~:(id,firstName,lastName,emailAddress)',
    'scope': 'r_liteprofile r_emailaddress',
}


async def get_oauth_user_info(provider: str, token: str) -> dict:
    """Get user info from OAuth provider."""
    config = {
        'google': GOOGLE_OAUTH_CONFIG,
        'microsoft': MICROSOFT_OAUTH_CONFIG,
        'linkedin': LINKEDIN_OAUTH_CONFIG,
    }.get(provider)
    
    if not config:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")
    
    async with httpx.AsyncClient() as client:
        headers = {'Authorization': f'Bearer {token}'}
        response = await client.get(config['userinfo_url'], headers=headers)
        response.raise_for_status()
        return response.json()


async def create_or_update_oauth_user(db: AsyncSession, provider: str, user_info: dict) -> User:
    """Create or update user from OAuth provider data."""
    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
    
    # Extract user data based on provider
    if provider == 'google':
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        provider_id = user_info.get('id')
    elif provider == 'microsoft':
        first_name = user_info.get('givenName', '')
        last_name = user_info.get('surname', '')
        email = user_info.get('mail') or user_info.get('userPrincipalName', email)
        provider_id = user_info.get('id')
    elif provider == 'linkedin':
        first_name = user_info.get('firstName', {}).get('localized', {}).get('en_US', '')
        last_name = user_info.get('lastName', {}).get('localized', {}).get('en_US', '')
        email = user_info.get('emailAddress', email)
        provider_id = user_info.get('id')
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        # Update OAuth ID if not set
        if provider == 'google' and not user.google_id:
            user.google_id = provider_id
        elif provider == 'microsoft' and not user.microsoft_id:
            user.microsoft_id = provider_id
        elif provider == 'linkedin' and not user.linkedin_id:
            user.linkedin_id = provider_id
    else:
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_verified=True,  # OAuth users are pre-verified
        )
        
        # Set OAuth ID
        if provider == 'google':
            user.google_id = provider_id
        elif provider == 'microsoft':
            user.microsoft_id = provider_id
        elif provider == 'linkedin':
            user.linkedin_id = provider_id
        
        db.add(user)
        await db.flush()
        
        # Create organization membership
        email_domain = email.split('@')[-1].lower()
        result = await db.execute(select(Organization).where(Organization.domain == email_domain))
        organization = result.scalar_one_or_none()
        
        if not organization:
            organization = Organization(
                name=f"{email_domain.title()} Organization",
                domain=email_domain
            )
            db.add(organization)
            await db.flush()
        
        member = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=UserRole.RECRUITER.value,
        )
        db.add(member)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with email validation and domain-based organization assignment.
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
    
    # Extract domain from email
    email_domain = user_data.email.split('@')[-1].lower()
    
    # Find organization by domain
    result = await db.execute(select(Organization).where(Organization.domain == email_domain))
    organization = result.scalar_one_or_none()
    
    if not organization:
        # Create new organization for this domain
        org_name = user_data.organization_name or f"{email_domain.title()} Organization"
        organization = Organization(
            name=org_name,
            domain=email_domain
        )
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
    user.last_login = datetime.now(datetime.UTC).isoformat()
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


@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Initiate OAuth login flow.
    """
    config = {
        'google': GOOGLE_OAUTH_CONFIG,
        'microsoft': MICROSOFT_OAUTH_CONFIG,
        'linkedin': LINKEDIN_OAUTH_CONFIG,
    }.get(provider)
    
    if not config or not config['client_id'] or config['client_id'] == 'your-' + provider + '-client-id-here':
        raise HTTPException(
            status_code=400, 
            detail=f"OAuth provider {provider} not configured. Please set {provider.upper()}_CLIENT_ID and {provider.upper()}_CLIENT_SECRET in your environment variables."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state with expiration (5 minutes)
    oauth_states[state] = {
        'provider': provider,
        'expires_at': time.time() + 300  # 5 minutes
    }
    
    # Clean up expired states
    current_time = time.time()
    expired_states = [s for s, data in oauth_states.items() if data['expires_at'] < current_time]
    for s in expired_states:
        del oauth_states[s]
    
    params = {
        'client_id': config['client_id'],
        'redirect_uri': str(request.url_for('oauth_callback', provider=provider)),
        'scope': config['scope'],
        'response_type': 'code',
        'state': state,
    }
    
    if provider == 'google':
        params['access_type'] = 'offline'
        params['prompt'] = 'consent'
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{config['authorize_url']}?{query_string}"
    
    return RedirectResponse(auth_url)


@router.get("/oauth/{provider}/callback", response_class=HTMLResponse)
async def oauth_callback(
    provider: str,
    code: str,
    state: Optional[str] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback and create/login user.
    """
    config = {
        'google': GOOGLE_OAUTH_CONFIG,
        'microsoft': MICROSOFT_OAUTH_CONFIG,
        'linkedin': LINKEDIN_OAUTH_CONFIG,
    }.get(provider)
    
    if not config:
        return HTMLResponse(f"""
        <html>
        <body>
        <script>
        alert('Invalid OAuth provider');
        window.location.href = '/auth/login';
        </script>
        </body>
        </html>
        """)
    
    # Validate state parameter
    if not state or state not in oauth_states:
        return HTMLResponse(f"""
        <html>
        <body>
        <script>
        alert('Invalid or missing state parameter');
        window.location.href = '/auth/login';
        </script>
        </body>
        </html>
        """)
    
    state_data = oauth_states[state]
    if state_data['provider'] != provider or state_data['expires_at'] < time.time():
        return HTMLResponse(f"""
        <html>
        <body>
        <script>
        alert('State validation failed');
        window.location.href = '/auth/login';
        </script>
        </body>
        </html>
        """)
    
    # Remove used state
    del oauth_states[state]
    
    # Exchange code for access token
    token_data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': str(request.url_for('oauth_callback', provider=provider)),
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(config['access_token_url'], data=token_data)
            response.raise_for_status()
            token_response = response.json()
        
        access_token = token_response.get('access_token')
        if not access_token:
            return HTMLResponse(f"""
            <html>
            <body>
            <script>
            alert('Failed to obtain access token');
            window.location.href = '/auth/login';
            </script>
            </body>
            </html>
            """)
        
        # Get user info
        user_info = await get_oauth_user_info(provider, access_token)
        
        # Create or update user
        user = await create_or_update_oauth_user(db, provider, user_info)
        
        # Get user's organization
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True)
            .limit(1)
        )
        member = result.scalar_one_or_none()
        org_id = str(member.organization_id) if member else None
        
        # Create tokens
        access_token_jwt = create_access_token(data={"sub": str(user.id), "org_id": org_id})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Update last login
        user.last_login = datetime.now(datetime.UTC).isoformat()
        await db.commit()
        
        # Return HTML that sets tokens and redirects
        frontend_url = settings.allowed_origins.split(',')[0].strip()  # Get first allowed origin
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Signing you in...</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #f8fafc;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}
                .spinner {{
                    border: 3px solid #e2e8f0;
                    border-top: 3px solid #3b82f6;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                .message {{
                    color: #374151;
                    margin-bottom: 1rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner"></div>
                <div class="message">Signing you in with {provider.title()}...</div>
                <div style="color: #6b7280; font-size: 0.875rem;">Please wait while we complete your authentication.</div>
            </div>
            <script>
                try {{
                    localStorage.setItem('access_token', '{access_token_jwt}');
                    localStorage.setItem('refresh_token', '{refresh_token}');
                    window.location.href = '{frontend_url}/dashboard?success=oauth_login';
                }} catch (error) {{
                    console.error('Failed to set tokens:', error);
                    window.location.href = '{frontend_url}/auth/login?error=oauth_failed';
                }}
            </script>
        </body>
        </html>
        """)
        
    except Exception as e:
        frontend_url = settings.allowed_origins.split(',')[0].strip()
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Failed</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #fef2f2;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    max-width: 400px;
                }}
                .error-icon {{
                    color: #ef4444;
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }}
                .title {{
                    color: #dc2626;
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                }}
                .message {{
                    color: #374151;
                    margin-bottom: 1.5rem;
                }}
                .button {{
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 0.375rem;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }}
                .button:hover {{
                    background: #2563eb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">⚠️</div>
                <div class="title">Authentication Failed</div>
                <div class="message">We couldn't sign you in with {provider.title()}. Please try again or contact support if the problem persists.</div>
                <a href="{frontend_url}/auth/login" class="button">Return to Sign In</a>
            </div>
            <script>
                // Auto-redirect after 5 seconds
                setTimeout(function() {{
                    window.location.href = '{frontend_url}/auth/login?error=oauth_failed';
                }}, 5000);
            </script>
        </body>
        </html>
        """)


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
