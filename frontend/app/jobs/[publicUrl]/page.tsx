'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import { formatDate } from '../../../lib/utils'
import { Button } from '../../../components/ui/button'

export default function PublicJobPage() {
  const params = useParams()
  const publicUrl = (params?.publicUrl || '') as string

  const {
    data: job,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['public-job', publicUrl],
    enabled: !!publicUrl,
    queryFn: async () => {
      const data = await apiClient.getPublicJob(publicUrl)
      return data
    },
  })

  if (!publicUrl) {
    return <p className="text-sm text-destructive">Missing job URL.</p>
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading job...</p>
  }

  if (error || !job) {
    return <p className="text-sm text-destructive">Job not found or not publicly available.</p>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <div className="rounded-lg bg-white p-8 shadow-sm">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
            <p className="mt-2 text-lg text-gray-600">
              {job.organization_name} · {job.location || 'Remote'} ·{' '}
              <span className="capitalize">{job.employment_type.replace('_', ' ')}</span>
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-[2fr,1fr]">
            <section className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-3">Job Description</h2>
                <p className="whitespace-pre-wrap text-gray-700">{job.description}</p>
              </div>

              {job.requirements && (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Requirements</h2>
                  <p className="whitespace-pre-wrap text-gray-700">{job.requirements}</p>
                </div>
              )}

              {job.responsibilities && (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Responsibilities</h2>
                  <p className="whitespace-pre-wrap text-gray-700">{job.responsibilities}</p>
                </div>
              )}
            </section>

            <aside className="space-y-6">
              <div className="rounded-lg border bg-gray-50 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h3>

                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium text-gray-500">Department</div>
                    <div className="text-sm text-gray-900">
                      {job.department || 'Not specified'}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm font-medium text-gray-500">Experience Level</div>
                    <div className="text-sm text-gray-900 capitalize">
                      {job.experience_level}
                    </div>
                  </div>

                  {(job.salary_min || job.salary_max) && (
                    <div>
                      <div className="text-sm font-medium text-gray-500">Salary Range</div>
                      <div className="text-sm text-gray-900">
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
                      <div className="text-sm font-medium text-gray-500 mb-2">Required Skills</div>
                      <div className="flex flex-wrap gap-2">
                        {job.skills_required.map((skill) => (
                          <span
                            key={skill}
                            className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  <Button className="w-full" size="lg">
                    Apply Now
                  </Button>
                </div>
              </div>

              <div className="text-xs text-gray-500 text-center">
                Posted {formatDate(job.created_at)}
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  )
}