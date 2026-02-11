"""User-related Pydantic schemas."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    title: Optional[str] = None
    timezone: str = "UTC"


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithOrganizations(UserResponse):
    """User with their organizations."""
    organizations: List["OrganizationMemberResponse"] = []


# Organization Schemas
class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    settings: Optional[dict] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""
    id: str
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Organization Member Schemas
class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    role: str


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for creating an organization member."""
    user_id: str


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating an organization member."""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[dict] = None


class OrganizationMemberResponse(OrganizationMemberBase):
    """Schema for organization member response."""
    id: str
    organization_id: str
    user_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
