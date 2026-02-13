'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import type { Candidate } from '../../../types'
import { formatDate } from '../../../lib/utils'
import {
  Users,
  MapPin,
  Briefcase,
  Mail,
  Phone,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  MessageSquare,
  Star
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

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

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName[0]}${lastName[0]}`.toUpperCase()
  }

  const getExperienceLevel = (years: number | null | undefined) => {
    if (!years && years !== 0) return 'Entry Level'
    if (years < 2) return 'Entry Level'
    if (years < 5) return 'Mid Level'
    if (years < 10) return 'Senior Level'
    return 'Expert Level'
  }

  const getRandomGradient = (index: number) => {
    const gradients = [
      'from-blue-500 to-purple-500',
      'from-purple-500 to-pink-500',
      'from-green-500 to-teal-500',
      'from-orange-500 to-red-500',
      'from-indigo-500 to-blue-500',
      'from-pink-500 to-rose-500',
    ]
    return gradients[index % gradients.length]
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Candidate Pool
          </h1>
          <p className="text-gray-600">
            Discover and manage top talent for your open positions
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="rounded-lg">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Link href="/dashboard/candidates/new">
            <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg rounded-lg">
              <Plus className="w-4 h-4 mr-2" />
              Add Candidate
            </Button>
          </Link>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <Input
          placeholder="Search candidates by name, skills, or location..."
          className="pl-10 py-3 rounded-xl border-gray-200 focus:border-purple-300 focus:ring-purple-200"
        />
      </div>

      {/* Candidates Grid */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 animate-pulse">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {error && !isLoading && (
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">
            <Users className="w-16 h-16 mx-auto text-red-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Failed to load candidates</h3>
            <p className="text-gray-600">Please try again later</p>
          </div>
          <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      )}

      {!isLoading && !error && candidates && candidates.length === 0 && (
        <div className="text-center py-12">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No candidates yet</h3>
          <p className="text-gray-600 mb-6">Start building your talent pool by adding candidates or importing from external sources</p>
          <Link href="/dashboard/candidates/new">
            <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg">
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Candidate
            </Button>
          </Link>
        </div>
      )}

      {!isLoading && !error && candidates && candidates.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {candidates.map((candidate, index) => (
            <div
              key={candidate.id}
              className="bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-200 overflow-hidden group"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 bg-gradient-to-r ${getRandomGradient(index)} rounded-full flex items-center justify-center text-white font-bold text-lg`}>
                      {getInitials(candidate.first_name, candidate.last_name)}
                    </div>
                    <div className="flex-1">
                      <Link
                        href={`/dashboard/candidates/${candidate.id}`}
                        className="text-lg font-bold text-gray-900 hover:text-purple-600 transition-colors group-hover:underline"
                      >
                        {candidate.first_name} {candidate.last_name}
                      </Link>
                      <p className="text-gray-600 text-sm">
                        {candidate.headline || 'Professional'}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" className="p-1 h-8 w-8 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="truncate">{candidate.email}</span>
                  </div>
                  {candidate.location && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{candidate.location}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Briefcase className="w-4 h-4 text-gray-400" />
                    <span>{getExperienceLevel(candidate.total_experience_years)}</span>
                    {candidate.total_experience_years && (
                      <span className="text-gray-500">
                        ({candidate.total_experience_years} yrs)
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="text-xs text-gray-500">
                    Added {formatDate(candidate.created_at)}
                  </div>
                  <div className="flex items-center gap-2">
                    <Link href={`/dashboard/candidates/${candidate.id}`}>
                      <Button variant="outline" size="sm" className="rounded-lg">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                    </Link>
                    <Button variant="outline" size="sm" className="rounded-lg">
                      <MessageSquare className="w-4 h-4 mr-1" />
                      Contact
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats Footer */}
      {!isLoading && !error && candidates && candidates.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Talent Pool Insights
              </h3>
              <p className="text-gray-600 text-sm">
                Track your candidate quality and hiring pipeline performance
              </p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{candidates.length}</div>
                <div className="text-xs text-gray-600">Total Candidates</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-pink-600">
                  {candidates.filter(c => c.total_experience_years && c.total_experience_years >= 5).length}
                </div>
                <div className="text-xs text-gray-600">Senior Level</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {Math.round(candidates.filter(c => c.total_experience_years).reduce((acc, c) => acc + (c.total_experience_years || 0), 0) / candidates.filter(c => c.total_experience_years).length) || 0}
                </div>
                <div className="text-xs text-gray-600">Avg Experience</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

