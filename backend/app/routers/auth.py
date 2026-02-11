from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from ..database import get_db
from ..schemas.auth import Token, UserCreate, UserLogin, RegisterResponse
from ..schemas.user import UserResponse
from ..utils.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from ..models.user import User, Organization, OrganizationMember, UserRole
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and create default organization
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified=False
    )
    db.add(db_user)
    await db.flush()  # Get user ID
    
    # Create default organization
    org_name = f"{user.first_name}'s Organization"
    organization = Organization(
        name=org_name,
        domain=user.email.split('@')[1],
        is_active=True
    )
    db.add(organization)
    await db.flush()
    
    # Link user to organization
    org_member = OrganizationMember(
        organization_id=organization.id,
        user_id=db_user.id,
        role=UserRole.ADMIN if user.role == "admin" else UserRole.RECRUITER,
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


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token
    """
    # Authenticate user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
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
