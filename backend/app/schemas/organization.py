"""
Pydantic schemas for organization management.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""
    name: str = Field(..., min_length=1, max_length=200)
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationMemberResponse(BaseModel):
    """Schema for organization member response."""
    id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: UUID
    name: str
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    members: Optional[List[OrganizationMemberResponse]] = None
    
    class Config:
        from_attributes = True


class OrganizationInvite(BaseModel):
    """Schema for inviting a member."""
    email: str
    role: str = Field(default="recruiter", pattern="^(admin|manager|recruiter|interviewer)$")


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating a member."""
    role: str = Field(..., pattern="^(admin|manager|recruiter|interviewer)$")
