'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/api'
import type { Job, Candidate } from '../../types'
import { formatDate } from '../../lib/utils'
import {
  Briefcase,
  Users,
  TrendingUp,
  Calendar,
  Sparkles,
  ArrowRight,
  Plus,
  Eye,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'

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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back! 👋
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your recruitment today
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg">
            <Plus className="w-4 h-4 mr-2" />
            Quick Actions
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <Briefcase className="w-8 h-8 opacity-80" />
            <TrendingUp className="w-5 h-5 opacity-60" />
          </div>
          <div className="text-3xl font-bold mb-1">24</div>
          <div className="text-blue-100 text-sm">Active Jobs</div>
          <div className="text-blue-200 text-xs mt-2">+12% from last month</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <Users className="w-8 h-8 opacity-80" />
            <Sparkles className="w-5 h-5 opacity-60" />
          </div>
          <div className="text-3xl font-bold mb-1">156</div>
          <div className="text-purple-100 text-sm">Total Candidates</div>
          <div className="text-purple-200 text-xs mt-2">+8% from last month</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <Calendar className="w-8 h-8 opacity-80" />
            <Clock className="w-5 h-5 opacity-60" />
          </div>
          <div className="text-3xl font-bold mb-1">12</div>
          <div className="text-green-100 text-sm">Interviews Today</div>
          <div className="text-green-200 text-xs mt-2">3 pending feedback</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="w-8 h-8 opacity-80" />
            <ArrowRight className="w-5 h-5 opacity-60" />
          </div>
          <div className="text-3xl font-bold mb-1">89%</div>
          <div className="text-orange-100 text-sm">Placement Rate</div>
          <div className="text-orange-200 text-xs mt-2">+5% from last month</div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Jobs */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Recent Jobs</h2>
                <p className="text-gray-600 text-sm mt-1">Your latest job postings</p>
              </div>
              <Link href="/dashboard/jobs">
                <Button variant="outline" size="sm" className="rounded-lg">
                  <Eye className="w-4 h-4 mr-2" />
                  View All
                </Button>
              </Link>
            </div>
          </div>

          <div className="p-6">
            {jobsLoading && (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            )}

            {jobsError && (
              <div className="text-center py-8">
                <div className="text-red-500 mb-2">Failed to load jobs</div>
                <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
                  Try Again
                </Button>
              </div>
            )}

            {!jobsLoading && !jobsError && (
              <div className="space-y-4">
                {jobs && jobs.length > 0 ? (
                  jobs.map((job) => (
                    <div
                      key={job.id}
                      className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 group"
                    >
                      <div className="flex-1">
                        <Link
                          href={`/dashboard/jobs/${job.id}`}
                          className="font-semibold text-gray-900 hover:text-blue-600 transition-colors group-hover:underline"
                        >
                          {job.title}
                        </Link>
                        <div className="flex items-center gap-4 mt-1">
                          <span className="text-sm text-gray-600">
                            {job.location || 'Remote'}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            job.status === 'open'
                              ? 'bg-green-100 text-green-700'
                              : job.status === 'draft'
                              ? 'bg-gray-100 text-gray-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {job.status}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">
                          {formatDate(job.created_at)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No jobs yet</h3>
                    <p className="text-gray-600 mb-4">Create your first job posting to get started</p>
                    <Link href="/dashboard/jobs">
                      <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white">
                        <Plus className="w-4 h-4 mr-2" />
                        Create Job
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Candidates */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Recent Candidates</h2>
                <p className="text-gray-600 text-sm mt-1">Latest applicant activity</p>
              </div>
              <Link href="/dashboard/candidates">
                <Button variant="outline" size="sm" className="rounded-lg">
                  <Eye className="w-4 h-4 mr-2" />
                  View All
                </Button>
              </Link>
            </div>
          </div>

          <div className="p-6">
            {candidatesLoading && (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            )}

            {candidatesError && (
              <div className="text-center py-8">
                <div className="text-red-500 mb-2">Failed to load candidates</div>
                <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
                  Try Again
                </Button>
              </div>
            )}

            {!candidatesLoading && !candidatesError && (
              <div className="space-y-4">
                {candidates && candidates.length > 0 ? (
                  candidates.map((candidate) => (
                    <div
                      key={candidate.id}
                      className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-purple-200 hover:shadow-md transition-all duration-200 group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                          {candidate.first_name[0]}{candidate.last_name[0]}
                        </div>
                        <div>
                          <Link
                            href={`/dashboard/candidates/${candidate.id}`}
                            className="font-semibold text-gray-900 hover:text-purple-600 transition-colors group-hover:underline"
                          >
                            {candidate.first_name} {candidate.last_name}
                          </Link>
                          <div className="text-sm text-gray-600">
                            {candidate.email}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">
                          {formatDate(candidate.created_at)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No candidates yet</h3>
                    <p className="text-gray-600 mb-4">New applicants will appear here</p>
                    <Link href="/dashboard/candidates">
                      <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Candidate
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Ready to accelerate your hiring?</h2>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Use AI-powered tools to find better candidates faster and streamline your entire recruitment process.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard/jobs">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-50 font-semibold px-8">
                <Briefcase className="w-5 h-5 mr-2" />
                Post a Job
              </Button>
            </Link>
            <Link href="/dashboard/candidates">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 font-semibold px-8">
                <Users className="w-5 h-5 mr-2" />
                Browse Candidates
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

