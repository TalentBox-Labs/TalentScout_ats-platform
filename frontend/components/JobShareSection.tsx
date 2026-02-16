'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { ShareLinksResponse, ShareLink } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Share2, Copy, Check, Linkedin, Twitter, Facebook, Mail } from 'lucide-react'

interface JobShareSectionProps {
  jobId: string
  jobTitle: string
}

export function JobShareSection({ jobId, jobTitle }: JobShareSectionProps) {
  const [shareLinks, setShareLinks] = useState<ShareLinksResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [copiedLink, setCopiedLink] = useState<string | null>(null)

  useEffect(() => {
    const fetchShareLinks = async () => {
      try {
        const links = await apiClient.getShareLinks(jobId)
        setShareLinks(links)
      } catch (error) {
        console.error('Failed to fetch share links:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchShareLinks()
  }, [jobId])

  const handleShare = async (platform: string, url: string) => {
    try {
      // Track the share
      await apiClient.trackShare(jobId, platform)

      // Open share URL in new window for social platforms
      if (platform !== 'copy') {
        window.open(url, '_blank', 'noopener,noreferrer')
      } else {
        // Copy to clipboard
        await navigator.clipboard.writeText(url)
        setCopiedLink(url)
        alert('Link copied to clipboard!')
        setTimeout(() => setCopiedLink(null), 2000)
      }
    } catch (error) {
      console.error('Failed to track share:', error)
      // Still open the share URL even if tracking fails
      if (platform !== 'copy') {
        window.open(url, '_blank', 'noopener,noreferrer')
      }
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'linkedin':
        return <Linkedin className="h-4 w-4" />
      case 'twitter':
        return <Twitter className="h-4 w-4" />
      case 'facebook':
        return <Facebook className="h-4 w-4" />
      case 'email':
        return <Mail className="h-4 w-4" />
      case 'copy':
        return copiedLink === shareLinks?.public_url ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />
      default:
        return <Share2 className="h-4 w-4" />
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'linkedin':
        return 'hover:bg-blue-600 hover:text-white'
      case 'twitter':
        return 'hover:bg-blue-400 hover:text-white'
      case 'facebook':
        return 'hover:bg-blue-700 hover:text-white'
      case 'email':
        return 'hover:bg-gray-600 hover:text-white'
      case 'copy':
        return copiedLink === shareLinks?.public_url ? 'bg-green-600 text-white' : 'hover:bg-gray-600 hover:text-white'
      default:
        return 'hover:bg-gray-600 hover:text-white'
    }
  }

  if (loading) {
    return (
      <Card className="w-80">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            Share this job
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-2">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!shareLinks) {
    return null
  }

  return (
    <Card className="w-80">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Share2 className="h-5 w-5" />
          Share this job
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {shareLinks.share_links.map((link: ShareLink) => (
          <Button
            key={link.platform}
            variant="outline"
            className={`w-full justify-start gap-2 transition-colors ${getPlatformColor(link.platform)}`}
            onClick={() => handleShare(link.platform, link.url)}
          >
            {getPlatformIcon(link.platform)}
            <span className="capitalize">{link.platform}</span>
          </Button>
        ))}

        {/* Public URL display */}
        <div className="pt-3 border-t">
          <p className="text-sm text-gray-600 mb-2">Public URL:</p>
          <div className="bg-gray-50 p-2 rounded text-xs font-mono break-all">
            {shareLinks.public_url}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}