'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/api'
import type { Job, Candidate } from '../../types'
import { formatDate } from '../../lib/utils'

export default function DashboardPage() {
  const {
    data: jobs,
    isLoading: jobsLoading,
    error: jobsError,
  } = useQuery({
    queryKey: ['jobs', { limit: 5 }],
    queryFn: async () => {
      const data = await apiClient.getJobs({ limit: 5 })
      return data as Job[]
    },
  })

  const {
    data: candidates,
    isLoading: candidatesLoading,
    error: candidatesError,
  } = useQuery({
    queryKey: ['candidates', { limit: 5 }],
    queryFn: async () => {
      const data = await apiClient.getCandidates({ limit: 5 })
      return data as Candidate[]
    },
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Quick overview of your jobs and candidates.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-medium">Recent Jobs</h2>
            <Link
              href="/dashboard/jobs"
              className="text-xs font-medium text-primary hover:underline"
            >
              View all
            </Link>
          </div>
          {jobsLoading && <p className="text-xs text-muted-foreground">Loading jobs...</p>}
          {jobsError && (
            <p className="text-xs text-destructive">Failed to load jobs.</p>
          )}
          {!jobsLoading && !jobsError && (
            <ul className="space-y-2 text-sm">
              {jobs && jobs.length > 0 ? (
                jobs.map((job) => (
                  <li
                    key={job.id}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <div>
                      <Link
                        href={`/dashboard/jobs/${job.id}`}
                        className="font-medium hover:underline"
                      >
                        {job.title}
                      </Link>
                      <p className="text-xs text-muted-foreground">
                        {job.location || 'Location not specified'} ·{' '}
                        <span className="capitalize">{job.status}</span>
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(job.created_at)}
                    </span>
                  </li>
                ))
              ) : (
                <p className="text-xs text-muted-foreground">
                  No jobs yet. Create your first job from the Jobs section.
                </p>
              )}
            </ul>
          )}
        </section>

        <section className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-medium">Recent Candidates</h2>
            <Link
              href="/dashboard/candidates"
              className="text-xs font-medium text-primary hover:underline"
            >
              View all
            </Link>
          </div>
          {candidatesLoading && (
            <p className="text-xs text-muted-foreground">Loading candidates...</p>
          )}
          {candidatesError && (
            <p className="text-xs text-destructive">Failed to load candidates.</p>
          )}
          {!candidatesLoading && !candidatesError && (
            <ul className="space-y-2 text-sm">
              {candidates && candidates.length > 0 ? (
                candidates.map((candidate) => (
                  <li
                    key={candidate.id}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <div>
                      <Link
                        href={`/dashboard/candidates/${candidate.id}`}
                        className="font-medium hover:underline"
                      >
                        {candidate.first_name} {candidate.last_name}
                      </Link>
                      <p className="text-xs text-muted-foreground">
                        {candidate.email}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(candidate.created_at)}
                    </span>
                  </li>
                ))
              ) : (
                <p className="text-xs text-muted-foreground">
                  No candidates yet. New applicants will appear here.
                </p>
              )}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}

