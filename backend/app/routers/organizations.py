"""
Organization management router for multi-tenant support.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.middleware.auth import get_current_membership, CurrentMembership, RoleChecker
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
    OrganizationInvite,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    List all organizations the current user belongs to.
    """
    result = await db.execute(
        select(Organization)
        .join(User)
        .where(User.id == membership.user.id)
        .options(selectinload(Organization.members))
    )
    organizations = result.scalars().all()
    
    return organizations


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization.
    The creating user becomes the admin of the organization.
    """
    new_org = Organization(
        name=org_data.name,
        settings=org_data.settings or {},
        is_active=True,
    )
    
    db.add(new_org)
    await db.flush()
    
    # Make current user the admin of this organization
    member = OrganizationMember(
        organization_id=new_org.id,
        user_id=membership.user.id,
        role=UserRole.ADMIN
    )
    db.add(member)
    await db.commit()
    await db.refresh(new_org)
    
    return new_org


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: UUID,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization details.
    """
    # Verify user has access to this organization
    if membership.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    
    result = await db.execute(
        select(Organization)
        .where(Organization.id == organization_id)
        .options(selectinload(Organization.members))
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    return organization


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: UUID,
    org_data: OrganizationUpdate,
    membership: CurrentMembership = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization details (admin only).
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Update fields
    if org_data.name is not None:
        organization.name = org_data.name
    if org_data.settings is not None:
        organization.settings = org_data.settings
    if org_data.is_active is not None:
        organization.is_active = org_data.is_active
    
    await db.commit()
    await db.refresh(organization)
    
    return organization


@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse)
async def invite_member(
    organization_id: UUID,
    invite_data: OrganizationInvite,
    membership: CurrentMembership = Depends(RoleChecker(["admin", "manager"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a team member to the organization.
    Admin and managers can invite members.
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == invite_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Check if user is already a member
        result = await db.execute(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == str(organization_id),
                    OrganizationMember.user_id == existing_user.id
                )
            )
        )
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization",
            )
        
        # Create new membership
        member = OrganizationMember(
            organization_id=str(organization_id),
            user_id=existing_user.id,
            role=invite_data.role
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member
    
    # TODO: Send invitation email with signup link
    # For now, return a message
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found. Invitation email will be sent (not implemented yet).",
    )


@router.patch("/{organization_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    organization_id: UUID,
    user_id: UUID,
    member_data: OrganizationMemberUpdate,
    membership: CurrentMembership = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member's role (admin only).
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    
    # Find the organization member record
    from app.models.user import OrganizationMember
    result = await db.execute(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id
            )
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this organization",
        )
    
    # Prevent self-demotion from admin
    if member.user_id == membership.user.id and member_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role",
        )
    
    member.role = member_data.role
    await db.commit()
    await db.refresh(member)
    
    return member


@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    organization_id: UUID,
    user_id: UUID,
    membership: CurrentMembership = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from the organization (admin only).
    """
    # Verify user has access to this organization
    if str(membership.organization_id) != str(organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    
    # Prevent self-removal
    if user_id == membership.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the organization",
        )
    
    # Find and remove the organization member record
    from app.models.user import OrganizationMember
    result = await db.execute(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id
            )
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this organization",
        )
    
    await db.delete(member)
    await db.commit()
