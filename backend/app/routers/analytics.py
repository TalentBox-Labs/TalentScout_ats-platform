"""
Analytics and reporting router for ATS platform.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, Organization, OrganizationMember
from app.models.application import Application
from app.models.job import Job, JobStage
from app.models.candidate import Candidate
from app.middleware.auth import get_current_user, RoleChecker

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=Dict[str, Any])
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive analytics for the organization.
    """
    # Get date ranges
    now = datetime.now(datetime.UTC)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Total applications
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.organization_id == current_user.organization_id
        )
    )
    total_applications = result.scalar() or 0

    # Total jobs
    result = await db.execute(
        select(func.count(Job.id)).where(
            Job.organization_id == current_user.organization_id
        )
    )
    total_jobs = result.scalar() or 0

    # Average time to hire (simplified - days between application and hire)
    # This is a simplified calculation - in reality you'd track status changes
    result = await db.execute(
        select(func.avg(
            func.extract('epoch', Application.updated_at - Application.created_at) / 86400
        )).where(and_(
            Application.organization_id == current_user.organization_id,
            Application.status == 'hired'
        ))
    )
    avg_time_to_hire = result.scalar() or 0

    # Conversion rate (hired / total applications)
    result = await db.execute(
        select(func.count(Application.id)).where(and_(
            Application.organization_id == current_user.organization_id,
            Application.status == 'hired'
        ))
    )
    hired_count = result.scalar() or 0
    conversion_rate = (hired_count / total_applications * 100) if total_applications > 0 else 0

    # Applications by stage
    stages_query = select(
        JobStage.name,
        func.count(Application.id).label('count')
    ).join(
        Application, Application.current_stage == JobStage.id
    ).where(
        Application.organization_id == current_user.organization_id
    ).group_by(JobStage.name)

    result = await db.execute(stages_query)
    stage_counts = {row.name: row.count for row in result}

    applications_by_stage = [
        {"name": stage_name, "value": count, "color": "#3B82F6"}
        for stage_name, count in stage_counts.items()
    ]

    # Top job postings
    jobs_query = select(
        Job.title,
        func.count(Application.id).label('application_count')
    ).join(
        Application, Job.id == Application.job_id
    ).where(
        Job.organization_id == current_user.organization_id
    ).group_by(
        Job.title
    ).order_by(
        desc('application_count')
    ).limit(5)

    result = await db.execute(jobs_query)
    applications_by_job = [
        {"name": row.title, "value": row.application_count}
        for row in result
    ]

    # Monthly applications (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Applications in this month
        result = await db.execute(
            select(func.count(Application.id)).where(and_(
                Application.organization_id == current_user.organization_id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ))
        )
        applications = result.scalar() or 0

        # Hires in this month
        result = await db.execute(
            select(func.count(Application.id)).where(and_(
                Application.organization_id == current_user.organization_id,
                Application.status == 'hired',
                Application.updated_at >= month_start,
                Application.updated_at <= month_end
            ))
        )
        hires = result.scalar() or 0

        monthly_data.append({
            "month": month_start.strftime("%b"),
            "applications": applications,
            "hires": hires,
        })

    return {
        "totalApplications": total_applications,
        "totalJobs": total_jobs,
        "avgTimeToHire": round(avg_time_to_hire, 1),
        "conversionRate": round(conversion_rate, 1),
        "applicationsByStage": applications_by_stage,
        "applicationsByJob": applications_by_job,
        "monthlyApplications": monthly_data,
    }


@router.get("/admin/system", response_model=Dict[str, Any])
async def get_system_analytics(
    current_user: User = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get system-wide analytics for administrators.
    """
    # Get date ranges
    now = datetime.now(datetime.UTC)
    thirty_days_ago = now - timedelta(days=30)

    # Total users across all organizations
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Total organizations
    result = await db.execute(select(func.count(Organization.id)))
    total_organizations = result.scalar() or 0

    # Total applications across all organizations
    result = await db.execute(select(func.count(Application.id)))
    total_applications = result.scalar() or 0

    # Total jobs across all organizations
    result = await db.execute(select(func.count(Job.id)))
    total_jobs = result.scalar() or 0

    # Total candidates
    result = await db.execute(select(func.count(Candidate.id)))
    total_candidates = result.scalar() or 0

    # New users in last 30 days
    result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    new_users_30d = result.scalar() or 0

    # New organizations in last 30 days
    result = await db.execute(
        select(func.count(Organization.id)).where(Organization.created_at >= thirty_days_ago)
    )
    new_orgs_30d = result.scalar() or 0

    # Top organizations by user count
    org_user_query = select(
        Organization.name,
        func.count(User.id).label('user_count')
    ).join(
        OrganizationMember, Organization.id == OrganizationMember.organization_id
    ).join(
        User, OrganizationMember.user_id == User.id
    ).where(
        OrganizationMember.is_active == True
    ).group_by(
        Organization.name
    ).order_by(
        desc('user_count')
    ).limit(10)

    result = await db.execute(org_user_query)
    top_orgs_by_users = [
        {"name": row.name, "users": row.user_count}
        for row in result
    ]

    # User registration trends (last 6 months)
    monthly_user_data = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        result = await db.execute(
            select(func.count(User.id)).where(and_(
                User.created_at >= month_start,
                User.created_at <= month_end
            ))
        )
        users = result.scalar() or 0

        result = await db.execute(
            select(func.count(Organization.id)).where(and_(
                Organization.created_at >= month_start,
                Organization.created_at <= month_end
            ))
        )
        orgs = result.scalar() or 0

        monthly_user_data.append({
            "month": month_start.strftime("%b %Y"),
            "newUsers": users,
            "newOrganizations": orgs,
        })

    # User roles distribution
    role_query = select(
        OrganizationMember.role,
        func.count(OrganizationMember.id).label('count')
    ).where(
        OrganizationMember.is_active == True
    ).group_by(
        OrganizationMember.role
    )

    result = await db.execute(role_query)
    role_distribution = [
        {"role": row.role, "count": row.count}
        for row in result
    ]

    return {
        "totalUsers": total_users,
        "totalOrganizations": total_organizations,
        "totalApplications": total_applications,
        "totalJobs": total_jobs,
        "totalCandidates": total_candidates,
        "newUsers30d": new_users_30d,
        "newOrganizations30d": new_orgs_30d,
        "topOrganizationsByUsers": top_orgs_by_users,
        "monthlyUserTrends": monthly_user_data,
        "userRoleDistribution": role_distribution,
    }


@router.get("/admin/users", response_model=Dict[str, Any])
async def get_user_management_data(
    current_user: User = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user management data for administrators.
    """
    # Get all users with their organization info
    user_query = select(
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.is_active,
        User.is_verified,
        User.created_at,
        User.last_login,
        Organization.name.label('organization_name'),
        OrganizationMember.role
    ).join(
        OrganizationMember, User.id == OrganizationMember.user_id
    ).join(
        Organization, OrganizationMember.organization_id == Organization.id
    ).where(
        OrganizationMember.is_active == True
    ).order_by(
        User.created_at.desc()
    )

    result = await db.execute(user_query)
    users_data = [
        {
            "id": str(row.id),
            "email": row.email,
            "name": f"{row.first_name} {row.last_name}",
            "organization": row.organization_name,
            "role": row.role,
            "isActive": row.is_active,
            "isVerified": row.is_verified,
            "createdAt": row.created_at.isoformat() if row.created_at else None,
            "lastLogin": row.last_login if row.last_login else None,
        }
        for row in result
    ]

    # User activity summary
    total_users = len(users_data)
    active_users = len([u for u in users_data if u["isActive"]])
    verified_users = len([u for u in users_data if u["isVerified"]])

    # Recent logins (last 7 days)
    seven_days_ago = datetime.now(datetime.UTC) - timedelta(days=7)
    recent_logins = len([
        u for u in users_data
        if u["lastLogin"] and datetime.fromisoformat(u["lastLogin"]) >= seven_days_ago
    ])

    return {
        "users": users_data,
        "summary": {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "verifiedUsers": verified_users,
            "recentLogins": recent_logins,
        }
    }