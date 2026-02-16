'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import type { Job } from '../../../types'
import { formatDate } from '../../../lib/utils'
import {
  Briefcase,
  MapPin,
  Clock,
  Users,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Share2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ShareButton } from '@/components/ShareButton'

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700 border-green-200'
      case 'draft':
        return 'bg-gray-100 text-gray-700 border-gray-200'
      case 'closed':
        return 'bg-red-100 text-red-700 border-red-200'
      default:
        return 'bg-blue-100 text-blue-700 border-blue-200'
    }
  }

  const getJobTypeIcon = (type: string) => {
    switch (type) {
      case 'full_time':
        return 'Full-time'
      case 'part_time':
        return 'Part-time'
      case 'contract':
        return 'Contract'
      case 'freelance':
        return 'Freelance'
      default:
        return type.replace('_', ' ')
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Job Postings
          </h1>
          <p className="text-gray-600">
            Manage your open positions and find the perfect candidates
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="rounded-lg">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Link href="/dashboard/jobs/new">
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg rounded-lg">
              <Plus className="w-4 h-4 mr-2" />
              Post New Job
            </Button>
          </Link>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <Input
          placeholder="Search jobs by title, department, or location..."
          className="pl-10 py-3 rounded-xl border-gray-200 focus:border-blue-300 focus:ring-blue-200"
        />
      </div>

      {/* Jobs Grid */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
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
            <Briefcase className="w-16 h-16 mx-auto text-red-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Failed to load jobs</h3>
            <p className="text-gray-600">Please try again later</p>
          </div>
          <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      )}

      {!isLoading && !error && jobs && jobs.length === 0 && (
        <div className="text-center py-12">
          <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-600 mb-6">Create your first job posting to get started with hiring</p>
          <Link href="/dashboard/jobs/new">
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg">
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Job
            </Button>
          </Link>
        </div>
      )}

      {!isLoading && !error && jobs && jobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-200 overflow-hidden group"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <Link
                      href={`/dashboard/jobs/${job.id}`}
                      className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors group-hover:underline"
                    >
                      {job.title}
                    </Link>
                    <p className="text-gray-600 text-sm mt-1">
                      {job.department || 'General'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-3 py-1 rounded-full font-medium border ${getStatusColor(job.status)}`}>
                      {job.status.replace('_', ' ')}
                    </span>
                    {job.is_public && (
                      <span className="text-xs px-2 py-1 rounded-full font-medium border bg-green-100 text-green-700 border-green-200">
                        Public
                      </span>
                    )}
                    <Button variant="ghost" size="sm" className="p-1 h-8 w-8 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span>{job.location || 'Remote'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="capitalize">{getJobTypeIcon(job.job_type)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span>0 applicants</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="text-xs text-gray-500">
                    Created {formatDate(job.created_at)}
                  </div>
                  <div className="flex items-center gap-2">
                    <Link href={`/dashboard/jobs/${job.id}`}>
                      <Button variant="outline" size="sm" className="rounded-lg">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                    </Link>
                    <Button variant="outline" size="sm" className="rounded-lg">
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                    {job.is_public && job.public_slug && (
                      <ShareButton
                        jobId={job.id}
                        jobTitle={job.title}
                        publicUrl={`${window.location.origin}/jobs/${job.public_slug}`}
                        variant="outline"
                        size="sm"
                        className="rounded-lg"
                      />
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats Footer */}
      {!isLoading && !error && jobs && jobs.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Job Performance Overview
              </h3>
              <p className="text-gray-600 text-sm">
                Track your hiring success and optimize your job postings
              </p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{jobs.length}</div>
                <div className="text-xs text-gray-600">Total Jobs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {jobs.filter(j => j.status === 'open').length}
                </div>
                <div className="text-xs text-gray-600">Active</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {jobs.filter(j => j.is_public).length}
                </div>
                <div className="text-xs text-gray-600">Public</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {jobs.reduce((sum, j) => sum + (j.view_count || 0), 0)}
                </div>
                <div className="text-xs text-gray-600">Total Views</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {jobs.reduce((sum, j) => sum + (j.share_count || 0), 0)}
                </div>
                <div className="text-xs text-gray-600">Total Shares</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

