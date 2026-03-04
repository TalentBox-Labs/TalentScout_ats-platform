'use client'

import { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Switch } from './ui/switch'
import { apiClient } from '../lib/api'
import type { Job } from '../types'
import { toast } from 'sonner'

interface ShareSectionProps {
  job: Job
}

export function ShareSection({ job }: ShareSectionProps) {
  const [isPublic, setIsPublic] = useState(job.is_public || false)
  const [publicUrl, setPublicUrl] = useState(job.public_url || '')
  const [loading, setLoading] = useState(false)

  const handlePublicToggle = async (checked: boolean) => {
    setLoading(true)
    try {
      const updatedJob = await apiClient.updateJob(job.id, { is_public: checked })
      setIsPublic(updatedJob.is_public)
      setPublicUrl(updatedJob.public_url || '')
      toast.success(checked ? 'Job is now public' : 'Job is now private')
    } catch (error) {
      toast.error('Failed to update job visibility')
    } finally {
      setLoading(false)
    }
  }

  const handleShare = async (platform: string) => {
    try {
      await apiClient.shareJob(job.id, platform)
      toast.success(`Shared on ${platform}`)
    } catch (error) {
      toast.error('Failed to track share')
    }
  }

  const copyPublicLink = () => {
    if (publicUrl) {
      const url = `${window.location.origin}/jobs/${publicUrl}`
      navigator.clipboard.writeText(url)
      toast.success('Public link copied to clipboard')
    }
  }

  const shareUrl = publicUrl ? `${window.location.origin}/jobs/${publicUrl}` : ''

  return (
    <div className="rounded-lg border bg-card p-4">
      <h2 className="text-lg font-semibold mb-4">Share Job Posting</h2>

      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Switch
            id="public"
            checked={isPublic}
            onCheckedChange={handlePublicToggle}
            disabled={loading}
          />
          <Label htmlFor="public">Make this job public</Label>
        </div>

        {isPublic && publicUrl && (
          <div className="space-y-2">
            <Label>Public Link</Label>
            <div className="flex space-x-2">
              <Input value={shareUrl} readOnly />
              <Button onClick={copyPublicLink} variant="outline">
                Copy
              </Button>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <Label>Share on Social Media</Label>
          <div className="flex space-x-2">
            <Button
              onClick={() => handleShare('linkedin')}
              variant="outline"
              size="sm"
              disabled={!isPublic}
            >
              LinkedIn
            </Button>
            <Button
              onClick={() => handleShare('twitter')}
              variant="outline"
              size="sm"
              disabled={!isPublic}
            >
              Twitter
            </Button>
            <Button
              onClick={() => handleShare('facebook')}
              variant="outline"
              size="sm"
              disabled={!isPublic}
            >
              Facebook
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}