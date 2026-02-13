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
from app.models.user import User
from app.models.application import Application
from app.models.job import Job, JobStage
from app.models.candidate import Candidate
from app.middleware.auth import get_current_user

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
    now = datetime.utcnow()
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