'use client'

import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../../lib/api'
import type { Job } from '../../../../types'
import { formatDate } from '../../../../lib/utils'
import { JobDashboardShare } from '../../../../components/JobDashboardShare'

export default function JobDetailPage() {
  const params = useParams()
  const jobId = (params?.id || '') as string

  const {
    data: job,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['job', jobId],
    enabled: !!jobId,
    queryFn: async () => {
      const data = await apiClient.getJob(jobId)
      return data as Job
    },
  })

  if (!jobId) {
    return <p className="text-sm text-destructive">Missing job ID.</p>
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading job...</p>
  }

  if (error || !job) {
    return <p className="text-sm text-destructive">Failed to load job.</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{job.title}</h1>
          <p className="text-sm text-muted-foreground">
            {job.location || 'Remote'} ·{' '}
            <span className="capitalize">{job.job_type.replace('_', ' ')}</span>
          </p>
        </div>
        <Link
          href="/dashboard/jobs"
          className="text-xs font-medium text-primary hover:underline"
        >
          Back to jobs
        </Link>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr,1fr,1fr]">
        <section className="space-y-4 rounded-lg border bg-card p-4">
          <div>
            <h2 className="text-sm font-semibold">Description</h2>
            <p className="mt-1 whitespace-pre-wrap text-sm text-muted-foreground">
              {job.description || 'No description provided.'}
            </p>
          </div>

          {job.requirements && (
            <div>
              <h2 className="text-sm font-semibold">Requirements</h2>
              <p className="mt-1 whitespace-pre-wrap text-sm text-muted-foreground">
                {job.requirements}
              </p>
            </div>
          )}

          {job.responsibilities && (
            <div>
              <h2 className="text-sm font-semibold">Responsibilities</h2>
              <p className="mt-1 whitespace-pre-wrap text-sm text-muted-foreground">
                {job.responsibilities}
              </p>
            </div>
          )}
        </section>

        <aside className="space-y-3 rounded-lg border bg-card p-4 text-sm">
          <div>
            <div className="text-xs font-semibold text-muted-foreground">
              Status
            </div>
            <div className="text-sm capitalize">{job.status.replace('_', ' ')}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-muted-foreground">
              Department
            </div>
            <div className="text-sm">
              {job.department || 'Not specified'}
            </div>
          </div>
          <div>
            <div className="text-xs font-semibold text-muted-foreground">
              Created
            </div>
            <div className="text-sm">{formatDate(job.created_at)}</div>
          </div>
          {(job.salary_min || job.salary_max) && (
            <div>
              <div className="text-xs font-semibold text-muted-foreground">
                Salary range
              </div>
              <div className="text-sm">
                {job.salary_min && job.salary_max
                  ? `${job.salary_min.toLocaleString()}–${job.salary_max.toLocaleString()} ${job.salary_currency}`
                  : job.salary_min
                    ? `${job.salary_min.toLocaleString()}+ ${job.salary_currency}`
                    : `${job.salary_max?.toLocaleString()} ${job.salary_currency}`}
              </div>
            </div>
          )}
          {job.skills_required && job.skills_required.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-muted-foreground">
                Required skills
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {job.skills_required.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-muted px-2 py-0.5 text-xs"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </aside>

        <aside className="space-y-4">
          <JobDashboardShare job={job} />
        </aside>
      </div>
    </div>
  )
}

