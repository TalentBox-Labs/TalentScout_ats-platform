'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import type { Candidate } from '../../../types'
import { formatDate } from '../../../lib/utils'

export default function CandidatesPage() {
  const {
    data: candidates,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['candidates'],
    queryFn: async () => {
      const data = await apiClient.getCandidates()
      return data as Candidate[]
    },
  })

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Candidates</h1>
          <p className="text-sm text-muted-foreground">
            Browse and manage your talent pool.
          </p>
        </div>
      </header>

      <div className="overflow-hidden rounded-lg border bg-card">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b bg-muted/60 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Location</th>
              <th className="px-4 py-3">Experience</th>
              <th className="px-4 py-3">Added</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-muted-foreground">
                  Loading candidates...
                </td>
              </tr>
            )}
            {error && !isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-destructive">
                  Failed to load candidates.
                </td>
              </tr>
            )}
            {!isLoading && !error && candidates && candidates.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-muted-foreground">
                  No candidates found.
                </td>
              </tr>
            )}
            {!isLoading &&
              !error &&
              candidates &&
              candidates.map((candidate) => (
                <tr key={candidate.id} className="border-t hover:bg-muted/40">
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/candidates/${candidate.id}`}
                      className="font-medium hover:underline"
                    >
                      {candidate.first_name} {candidate.last_name}
                    </Link>
                    <div className="text-xs text-muted-foreground">
                      {candidate.headline || 'No headline'}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs">{candidate.email}</td>
                  <td className="px-4 py-3 text-xs">
                    {candidate.location || 'Location not specified'}
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {(candidate.years_of_experience ?? candidate.total_experience_years) != null
                      ? `${candidate.years_of_experience ?? candidate.total_experience_years} yrs`
                      : 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {formatDate(candidate.created_at)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

