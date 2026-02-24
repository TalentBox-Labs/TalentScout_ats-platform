'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Job, ShareLinksResponse } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Share2, Eye, Users, Globe, Lock, Copy, Check } from 'lucide-react'
import { JobShareSection } from '@/components/JobShareSection'

interface JobDashboardShareProps {
  job: Job
}

export function JobDashboardShare({ job }: JobDashboardShareProps) {
  const [showShareSection, setShowShareSection] = useState(false)
  const [copiedLink, setCopiedLink] = useState(false)
  const queryClient = useQueryClient()

  const publishMutation = useMutation({
    mutationFn: () => apiClient.publishJobPublic(job.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', job.id] })
    },
  })

  const unpublishMutation = useMutation({
    mutationFn: () => apiClient.unpublishJob(job.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', job.id] })
      setShowShareSection(false)
    },
  })

  const salaryVisibilityMutation = useMutation({
    mutationFn: (showSalary: boolean) => apiClient.updateSalaryVisibility(job.id, showSalary),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', job.id] })
    },
  })

  const handlePublishToggle = async () => {
    if (job.is_public) {
      await unpublishMutation.mutateAsync()
    } else {
      await publishMutation.mutateAsync()
    }
  }

  const handleSalaryVisibilityToggle = async (checked: boolean) => {
    await salaryVisibilityMutation.mutateAsync(checked)
  }

  const copyPublicUrl = async () => {
    if (job.public_slug) {
      const url = `${window.location.origin}/jobs/${job.public_slug}`
      await navigator.clipboard.writeText(url)
      setCopiedLink(true)
      setTimeout(() => setCopiedLink(false), 2000)
    }
  }

  const isLoading = publishMutation.isPending || unpublishMutation.isPending || salaryVisibilityMutation.isPending

  return (
    <div className="space-y-4">
      {/* Public Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {job.is_public ? <Globe className="h-5 w-5 text-green-600" /> : <Lock className="h-5 w-5 text-gray-400" />}
            Public Job Posting
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">
                {job.is_public ? 'Job is publicly visible' : 'Job is private'}
              </p>
              <p className="text-xs text-muted-foreground">
                {job.is_public
                  ? 'Anyone with the link can view this job posting'
                  : 'Only team members can view this job'
                }
              </p>
            </div>
            <Button
              onClick={handlePublishToggle}
              disabled={isLoading || job.status !== 'open'}
              variant={job.is_public ? 'destructive' : 'default'}
              size="sm"
            >
              {isLoading ? '...' : job.is_public ? 'Unpublish' : 'Publish Publicly'}
            </Button>
          </div>

          {job.status !== 'open' && (
            <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
              Only open jobs can be published publicly
            </p>
          )}
        </CardContent>
      </Card>

      {/* Public Job Stats */}
      {job.is_public && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Public Engagement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{job.view_count || 0}</div>
                <div className="text-xs text-muted-foreground">Views</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{job.share_count || 0}</div>
                <div className="text-xs text-muted-foreground">Shares</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Public URL */}
      {job.is_public && job.public_slug && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Public URL
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <code className="flex-1 text-xs bg-muted p-2 rounded font-mono">
                {`${window.location.origin}/jobs/${job.public_slug}`}
              </code>
              <Button
                size="sm"
                variant="outline"
                onClick={copyPublicUrl}
                className="shrink-0"
              >
                {copiedLink ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowShareSection(!showShareSection)}
              className="w-full"
            >
              <Share2 className="h-4 w-4 mr-2" />
              {showShareSection ? 'Hide' : 'Show'} Share Options
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Share Section */}
      {showShareSection && job.is_public && (
        <Card>
          <CardHeader>
            <CardTitle>Share This Job</CardTitle>
          </CardHeader>
          <CardContent>
            <JobShareSection jobId={job.id} jobTitle={job.title} />
          </CardContent>
        </Card>
      )}

      {/* Salary Visibility */}
      {job.is_public && (
        <Card>
          <CardHeader>
            <CardTitle>Salary Visibility</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium">Show salary on public page</p>
                <p className="text-xs text-muted-foreground">
                  {job.show_salary_public
                    ? 'Salary information is visible to applicants'
                    : 'Salary information is hidden from public view'
                  }
                </p>
              </div>
              <Switch
                checked={job.show_salary_public || false}
                onCheckedChange={handleSalaryVisibilityToggle}
                disabled={isLoading}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Share Metadata */}
      {job.is_public && job.share_metadata && Object.keys(job.share_metadata).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Share Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(job.share_metadata).map(([platform, count]) => (
                <div key={platform} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{platform}</span>
                  <Badge variant="secondary">{count as number}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}