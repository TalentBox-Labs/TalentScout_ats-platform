'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import type { Job } from '../../../types'
import { formatDate } from '../../../lib/utils'

export default function JobsPage() {
  const {
    data: jobs,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const data = await apiClient.getJobs()
      return data as Job[]
    },
  })

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
          <p className="text-sm text-muted-foreground">
            Browse and manage open roles.
          </p>
        </div>
      </header>

      <div className="overflow-hidden rounded-lg border bg-card">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b bg-muted/60 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Location</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Created</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-muted-foreground">
                  Loading jobs...
                </td>
              </tr>
            )}
            {error && !isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-destructive">
                  Failed to load jobs.
                </td>
              </tr>
            )}
            {!isLoading && !error && jobs && jobs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-muted-foreground">
                  No jobs found.
                </td>
              </tr>
            )}
            {!isLoading &&
              !error &&
              jobs &&
              jobs.map((job) => (
                <tr key={job.id} className="border-t hover:bg-muted/40">
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/jobs/${job.id}`}
                      className="font-medium hover:underline"
                    >
                      {job.title}
                    </Link>
                    <div className="text-xs text-muted-foreground">
                      {job.department || 'No department'}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs capitalize">
                    {job.status.replace('_', ' ')}
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {job.location || 'Remote'}
                  </td>
                  <td className="px-4 py-3 text-xs capitalize">
                    {job.job_type.replace('_', ' ')}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {formatDate(job.created_at)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

