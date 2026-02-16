'use client'

import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { FormEvent, Suspense, useState, useEffect } from 'react'
import { apiClient } from '../../../lib/api'
import { Button } from '@/components/ui/button'
import { Mail, Chrome, Building2, Linkedin } from 'lucide-react'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [oauthLoading, setOauthLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Check for OAuth errors in URL
  useEffect(() => {
    const errorParam = searchParams.get('error')
    const successParam = searchParams.get('success')
    
    if (errorParam === 'oauth_failed') {
      setError('OAuth authentication failed. Please try again.')
    } else if (successParam === 'oauth_login') {
      // Clear any existing errors on successful OAuth redirect
      setError(null)
    }
  }, [searchParams])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await apiClient.login(email, password)
      const next = searchParams.get('next') || '/dashboard'
      router.push(next)
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        'Unable to sign in. Please check your credentials and try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthLogin = async (provider: string) => {
    setOauthLoading(provider)
    setError(null)
    try {
      apiClient.oauthLogin(provider)
      // The page will redirect to OAuth provider
    } catch (err: any) {
      const message = err?.response?.data?.detail || 'Failed to initiate OAuth login'
      setError(message)
      setOauthLoading(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Access your ATS dashboard with your account.
        </p>
      </div>

      {/* OAuth Buttons */}
      <div className="space-y-3">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Continue with
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-2">
          <Button
            variant="outline"
            onClick={() => handleOAuthLogin('google')}
            className="w-full"
            type="button"
            disabled={oauthLoading !== null}
          >
            <Chrome className="mr-2 h-4 w-4" />
            {oauthLoading === 'google' ? 'Connecting...' : 'Google'}
          </Button>

          <Button
            variant="outline"
            onClick={() => handleOAuthLogin('microsoft')}
            className="w-full"
            type="button"
            disabled={oauthLoading !== null}
          >
            <Building2 className="mr-2 h-4 w-4" />
            {oauthLoading === 'microsoft' ? 'Connecting...' : 'Microsoft'}
          </Button>

          <Button
            variant="outline"
            onClick={() => handleOAuthLogin('linkedin')}
            className="w-full"
            type="button"
            disabled={oauthLoading !== null}
          >
            <Linkedin className="mr-2 h-4 w-4" />
            {oauthLoading === 'linkedin' ? 'Connecting...' : 'LinkedIn'}
          </Button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Or continue with email
            </span>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          />
        </div>
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        <Button
          type="submit"
          className="mt-2 w-full"
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </Button>
      </form>

      <p className="text-center text-xs text-muted-foreground">
        Don&apos;t have an account?{' '}
        <Link href="/auth/register" className="text-primary hover:underline">
          Create one
        </Link>
      </p>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="text-sm text-muted-foreground">Loading...</div>}>
      <LoginForm />
    </Suspense>
  )
}

