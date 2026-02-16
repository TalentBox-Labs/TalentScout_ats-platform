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
from app.middleware.auth import get_current_membership, CurrentMembership

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=Dict[str, Any])
async def get_analytics(
    membership: CurrentMembership = Depends(get_current_membership),
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
        select(func.count(Application.id))
        .join(Job, Application.job_id == Job.id)
        .where(Job.organization_id == membership.organization_id)
    )
    total_applications = result.scalar() or 0

    # Total jobs
    result = await db.execute(
        select(func.count(Job.id)).where(
            Job.organization_id == membership.organization_id
        )
    )
    total_jobs = result.scalar() or 0

    # Average time to hire (simplified - days between application and hire)
    # This is a simplified calculation - in reality you'd track status changes
    result = await db.execute(
        select(func.avg(
            func.extract('epoch', Application.updated_at - Application.created_at) / 86400
        ))
        .join(Job, Application.job_id == Job.id)
        .where(and_(
            Job.organization_id == membership.organization_id,
            Application.status == 'hired'
        ))
    )
    avg_time_to_hire = result.scalar() or 0

    # Conversion rate (hired / total applications)
    result = await db.execute(
        select(func.count(Application.id))
        .join(Job, Application.job_id == Job.id)
        .where(and_(
            Job.organization_id == membership.organization_id,
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
    ).join(
        Job, Application.job_id == Job.id
    ).where(
        Job.organization_id == membership.organization_id
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
        Job.organization_id == membership.organization_id
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
            select(func.count(Application.id))
            .join(Job, Application.job_id == Job.id)
            .where(and_(
                Job.organization_id == membership.organization_id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ))
        )
        applications = result.scalar() or 0

        # Hires in this month
        result = await db.execute(
            select(func.count(Application.id))
            .join(Job, Application.job_id == Job.id)
            .where(and_(
                Job.organization_id == membership.organization_id,
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


@router.get("/public-jobs", response_model=Dict[str, Any])
async def get_public_jobs_analytics(
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analytics for public job postings.
    """
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    # Public jobs overview
    result = await db.execute(
        select(
            func.count(Job.id).label('total_public_jobs'),
            func.sum(Job.view_count).label('total_views'),
            func.sum(Job.share_count).label('total_shares'),
            func.avg(Job.view_count).label('avg_views_per_job'),
            func.avg(Job.share_count).label('avg_shares_per_job')
        ).where(and_(
            Job.organization_id == membership.organization_id,
            Job.is_public == True
        ))
    )
    public_jobs_stats = result.first()

    # Top performing public jobs by views
    top_jobs_query = select(
        Job.title,
        Job.view_count,
        Job.share_count,
        Job.created_at,
        Job.published_at
    ).where(and_(
        Job.organization_id == membership.organization_id,
        Job.is_public == True
    )).order_by(
        desc(Job.view_count)
    ).limit(10)

    result = await db.execute(top_jobs_query)
    top_jobs_by_views = [
        {
            "title": row.title,
            "views": row.view_count,
            "shares": row.share_count,
            "published_at": row.published_at,
            "days_live": (now - row.published_at).days if row.published_at else None
        }
        for row in result
    ]

    # Share performance by platform
    result = await db.execute(
        select(Job.share_metadata)
        .where(and_(
            Job.organization_id == membership.organization_id,
            Job.is_public == True,
            Job.share_metadata.isnot(None)
        ))
    )

    platform_shares = {}
    for row in result:
        metadata = row.share_metadata or {}
        for platform, count in metadata.items():
            platform_shares[platform] = platform_shares.get(platform, 0) + count

    share_by_platform = [
        {"platform": platform, "shares": count}
        for platform, count in sorted(platform_shares.items(), key=lambda x: x[1], reverse=True)
    ]

    # Public job engagement over time (last 30 days)
    engagement_data = []
    for i in range(29, -1, -1):
        date = (now - timedelta(days=i)).date()

        # Jobs published on this date
        result = await db.execute(
            select(func.count(Job.id))
            .where(and_(
                Job.organization_id == membership.organization_id,
                Job.is_public == True,
                func.date(Job.published_at) == date
            ))
        )
        jobs_published = result.scalar() or 0

        # Views on jobs published in last 30 days
        result = await db.execute(
            select(func.sum(Job.view_count))
            .where(and_(
                Job.organization_id == membership.organization_id,
                Job.is_public == True,
                Job.published_at >= thirty_days_ago
            ))
        )
        total_views = result.scalar() or 0

        engagement_data.append({
            "date": date.isoformat(),
            "jobs_published": jobs_published,
            "total_views": total_views,
        })

    return {
        "overview": {
            "totalPublicJobs": public_jobs_stats.total_public_jobs or 0,
            "totalViews": public_jobs_stats.total_views or 0,
            "totalShares": public_jobs_stats.total_shares or 0,
            "avgViewsPerJob": round(public_jobs_stats.avg_views_per_job or 0, 1),
            "avgSharesPerJob": round(public_jobs_stats.avg_shares_per_job or 0, 1),
        },
        "topJobsByViews": top_jobs_by_views,
        "shareByPlatform": share_by_platform,
        "engagementOverTime": engagement_data,
    }


@router.get("/public-jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_analytics(
    job_id: str,
    membership: CurrentMembership = Depends(get_current_membership),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed analytics for a specific public job.
    """
    result = await db.execute(
        select(Job).where(and_(
            Job.id == job_id,
            Job.organization_id == membership.organization_id,
            Job.is_public == True
        ))
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Public job not found"
        )

    # Calculate engagement metrics
    days_live = (datetime.utcnow() - job.published_at).days if job.published_at else 0
    views_per_day = job.view_count / max(days_live, 1)
    shares_per_day = job.share_count / max(days_live, 1)

    # Share distribution by platform
    share_distribution = []
    if job.share_metadata:
        for platform, count in job.share_metadata.items():
            share_distribution.append({
                "platform": platform,
                "count": count,
                "percentage": round((count / job.share_count * 100), 1) if job.share_count > 0 else 0
            })

    return {
        "jobId": job.id,
        "title": job.title,
        "publishedAt": job.published_at,
        "daysLive": days_live,
        "metrics": {
            "views": job.view_count,
            "shares": job.share_count,
            "viewsPerDay": round(views_per_day, 2),
            "sharesPerDay": round(shares_per_day, 2),
            "shareToViewRatio": round((job.share_count / max(job.view_count, 1)), 3),
        },
        "shareDistribution": sorted(share_distribution, key=lambda x: x['count'], reverse=True),
    }