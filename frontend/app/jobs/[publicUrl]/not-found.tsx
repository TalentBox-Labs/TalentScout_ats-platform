'use client'

import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Job Not Found</h1>
        <p className="text-gray-600 mb-6 max-w-md">
          The job posting you're looking for doesn't exist or may have been removed.
        </p>
        <div className="space-x-4">
          <Button onClick={() => window.history.back()}>
            Go Back
          </Button>
          <Button variant="outline" onClick={() => window.location.href = '/'}>
            Browse Jobs
          </Button>
        </div>
      </div>
    </div>
  )
}