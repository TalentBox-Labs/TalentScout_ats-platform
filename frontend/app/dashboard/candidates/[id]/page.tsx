'use client'

import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../../lib/api'
import type { Candidate } from '../../../../types'
import { formatDate } from '../../../../lib/utils'

export default function CandidateDetailPage() {
  const params = useParams()
  const candidateId = (params?.id || '') as string

  const {
    data: candidate,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['candidate', candidateId],
    enabled: !!candidateId,
    queryFn: async () => {
      const data = await apiClient.getCandidate(candidateId)
      return data as Candidate
    },
  })

  if (!candidateId) {
    return <p className="text-sm text-destructive">Missing candidate ID.</p>
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading candidate...</p>
  }

  if (error || !candidate) {
    return <p className="text-sm text-destructive">Failed to load candidate.</p>
  }

  const fullName = `${candidate.first_name} ${candidate.last_name}`

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{fullName}</h1>
          <p className="text-sm text-muted-foreground">
            {candidate.headline || 'No headline'} · {candidate.location || 'No location'}
          </p>
        </div>
        <Link
          href="/dashboard/candidates"
          className="text-xs font-medium text-primary hover:underline"
        >
          Back to candidates
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-[2fr,1fr]">
        <section className="space-y-4 rounded-lg border bg-card p-4 text-sm">
          <div>
            <h2 className="text-sm font-semibold">Summary</h2>
            <p className="mt-1 whitespace-pre-wrap text-muted-foreground">
              {candidate.summary || 'No summary provided.'}
            </p>
          </div>

          <div>
            <h2 className="text-sm font-semibold">Contact</h2>
            <div className="mt-1 space-y-1 text-muted-foreground">
              <div>Email: {candidate.email}</div>
              {candidate.phone && <div>Phone: {candidate.phone}</div>}
              {candidate.linkedin_url && (
                <div>
                  LinkedIn:{' '}
                  <a
                    href={candidate.linkedin_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary hover:underline"
                  >
                    {candidate.linkedin_url}
                  </a>
                </div>
              )}
              {candidate.github_url && (
                <div>
                  GitHub:{' '}
                  <a
                    href={candidate.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary hover:underline"
                  >
                    {candidate.github_url}
                  </a>
                </div>
              )}
            </div>
          </div>

          {candidate.resume_url && (
            <div>
              <h2 className="text-sm font-semibold">Resume</h2>
              <p className="mt-1 text-muted-foreground break-all">
                {candidate.resume_url}
              </p>
            </div>
          )}
        </section>

        <aside className="space-y-3 rounded-lg border bg-card p-4 text-sm">
          <div>
            <div className="text-xs font-semibold text-muted-foreground">
              Created
            </div>
            <div className="text-sm">{formatDate(candidate.created_at)}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-muted-foreground">
              Experience
            </div>
            <div className="text-sm">
              {(candidate.years_of_experience ?? candidate.total_experience_years) != null
                ? `${candidate.years_of_experience ?? candidate.total_experience_years} years`
                : 'Not specified'}
            </div>
          </div>
          {candidate.tags && candidate.tags.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-muted-foreground">
                Tags
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {candidate.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-muted px-2 py-0.5 text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

