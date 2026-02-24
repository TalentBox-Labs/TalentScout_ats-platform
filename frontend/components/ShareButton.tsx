'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Share2, Copy, Check } from 'lucide-react'

interface ShareButtonProps {
  jobId: string
  jobTitle: string
  publicUrl: string
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'sm' | 'default' | 'lg'
  className?: string
}

export function ShareButton({
  jobId,
  jobTitle,
  publicUrl,
  variant = 'outline',
  size = 'sm',
  className = ''
}: ShareButtonProps) {
  const [copied, setCopied] = useState(false)

  const trackShareMutation = useMutation({
    mutationFn: (platform: string) => apiClient.trackShare(jobId, platform),
  })

  const handleShare = async (platform: string) => {
    try {
      if (platform === 'copy') {
        await navigator.clipboard.writeText(publicUrl)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } else {
        // Track the share
        await trackShareMutation.mutateAsync(platform)
        // Open share URL
        const shareUrls: Record<string, string> = {
          linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(publicUrl)}`,
          twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(jobTitle)}&url=${encodeURIComponent(publicUrl)}`,
          facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(publicUrl)}`,
          email: `mailto:?subject=${encodeURIComponent(jobTitle)}&body=${encodeURIComponent(publicUrl)}`,
        }
        window.open(shareUrls[platform], '_blank', 'noopener,noreferrer')
      }
    } catch (error) {
      console.error('Failed to share:', error)
    }
  }

  if (copied) {
    return (
      <Button
        variant={variant}
        size={size}
        className={className}
        disabled
      >
        <Check className="w-4 h-4 mr-1" />
        Copied!
      </Button>
    )
  }

  return (
    <div className="flex items-center gap-1">
      {/* Quick copy button */}
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={() => handleShare('copy')}
        title="Copy job link"
      >
        <Share2 className="w-4 h-4 mr-1" />
        Share
      </Button>
    </div>
  )
}