'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '../../../../../lib/api'

export default function GoogleCallback() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // The backend callback should redirect with tokens or handle the flow
        // For now, we'll assume the backend handles the OAuth flow and redirects back
        // In a full implementation, you'd parse URL params or handle the OAuth response
        
        // Check if we have tokens in URL params (if backend redirects with them)
        const urlParams = new URLSearchParams(window.location.search)
        const accessToken = urlParams.get('access_token')
        const refreshToken = urlParams.get('refresh_token')
        
        if (accessToken && refreshToken) {
          // Store tokens
          localStorage.setItem('access_token', accessToken)
          localStorage.setItem('refresh_token', refreshToken)
          
          // Set auth header for future requests
          apiClient.setAuthToken(accessToken)
          
          // Redirect to dashboard
          router.push('/dashboard')
        } else {
          // If no tokens, redirect to login with error
          setError('OAuth authentication failed')
          setTimeout(() => router.push('/auth/login'), 2000)
        }
      } catch (err) {
        setError('Authentication failed')
        setTimeout(() => router.push('/auth/login'), 2000)
      }
    }

    handleCallback()
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 sm:p-8 text-center">
          {error ? (
            <div className="space-y-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Authentication Failed</h1>
              <p className="text-gray-600">{error}</p>
              <p className="text-sm text-gray-500">Redirecting to login...</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto animate-spin">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Signing you in...</h1>
              <p className="text-gray-600">Please wait while we complete your authentication.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}