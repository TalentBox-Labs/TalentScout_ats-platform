import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center space-y-8 text-center">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              AI-First <span className="text-blue-600">Recruitment</span>
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-600 md:text-xl dark:text-gray-300">
              Modern Application Tracking System powered by artificial intelligence.
              Hire faster, smarter, and more efficiently.
            </p>
          </div>
          <div className="space-x-4">
            <Link href="/dashboard">
              <Button size="lg" className="h-12 px-8">
                Get Started
              </Button>
            </Link>
            <Link href="/auth/login">
              <Button size="lg" variant="outline" className="h-12 px-8">
                Sign In
              </Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3 mt-16">
            <div className="space-y-2">
              <div className="flex justify-center">
                <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                  <svg
                    className="h-6 w-6 text-blue-600 dark:text-blue-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                </div>
              </div>
              <h3 className="font-bold">Smart Parsing</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                AI-powered resume parsing extracts data automatically
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-center">
                <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                  <svg
                    className="h-6 w-6 text-blue-600 dark:text-blue-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
              </div>
              <h3 className="font-bold">Intelligent Matching</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Match candidates to jobs using semantic search
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-center">
                <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
                  <svg
                    className="h-6 w-6 text-blue-600 dark:text-blue-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
              <h3 className="font-bold">Automated Screening</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Let AI screen candidates and generate insights
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
