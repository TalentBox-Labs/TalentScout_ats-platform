"""Authentication-related Pydantic schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = "recruiter"


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_name: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict
    organization: Optional[dict] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response."""
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str  # Subject (user ID)
    type: str  # Token type (access/refresh)
    exp: int  # Expiration timestamp
    org_id: Optional[str] = None  # Current organization ID
