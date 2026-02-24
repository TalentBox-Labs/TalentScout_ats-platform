<<<<<<< HEAD
'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../../lib/api'
import { formatDate } from '../../../lib/utils'
import { Button } from '../../../components/ui/button'

export default function PublicJobPage() {
  const params = useParams()
  const publicUrl = (params?.publicUrl || '') as string

  const {
    data: job,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['public-job', publicUrl],
    enabled: !!publicUrl,
    queryFn: async () => {
      const data = await apiClient.getPublicJob(publicUrl)
      return data
    },
  })

  if (!publicUrl) {
    return <p className="text-sm text-destructive">Missing job URL.</p>
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading job...</p>
  }

  if (error || !job) {
    return <p className="text-sm text-destructive">Job not found or not publicly available.</p>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <div className="rounded-lg bg-white p-8 shadow-sm">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
            <p className="mt-2 text-lg text-gray-600">
              {job.organization_name} · {job.location || 'Remote'} ·{' '}
              <span className="capitalize">{job.employment_type.replace('_', ' ')}</span>
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-[2fr,1fr]">
            <section className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-3">Job Description</h2>
                <p className="whitespace-pre-wrap text-gray-700">{job.description}</p>
              </div>

              {job.requirements && (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Requirements</h2>
                  <p className="whitespace-pre-wrap text-gray-700">{job.requirements}</p>
                </div>
              )}

              {job.responsibilities && (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">Responsibilities</h2>
                  <p className="whitespace-pre-wrap text-gray-700">{job.responsibilities}</p>
                </div>
              )}
            </section>

            <aside className="space-y-6">
              <div className="rounded-lg border bg-gray-50 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h3>

                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium text-gray-500">Department</div>
                    <div className="text-sm text-gray-900">
                      {job.department || 'Not specified'}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm font-medium text-gray-500">Experience Level</div>
                    <div className="text-sm text-gray-900 capitalize">
                      {job.experience_level}
                    </div>
                  </div>

                  {(job.salary_min || job.salary_max) && (
                    <div>
                      <div className="text-sm font-medium text-gray-500">Salary Range</div>
                      <div className="text-sm text-gray-900">
                        {job.salary_min && job.salary_max
                          ? `${job.salary_min.toLocaleString()}–${job.salary_max.toLocaleString()} ${job.salary_currency}`
                          : job.salary_min
                            ? `${job.salary_min.toLocaleString()}+ ${job.salary_currency}`
                            : `${job.salary_max?.toLocaleString()} ${job.salary_currency}`}
                      </div>
                    </div>
                  )}

                  {job.skills_required && job.skills_required.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-gray-500 mb-2">Required Skills</div>
                      <div className="flex flex-wrap gap-2">
                        {job.skills_required.map((skill: string) => (
                          <span
                            key={skill}
                            className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  <Button className="w-full" size="lg">
                    Apply Now
                  </Button>
                </div>
              </div>

              <div className="text-xs text-gray-500 text-center">
                Posted {formatDate(job.created_at)}
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
=======
import { notFound } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { PublicJob } from '@/types'
import { PublicJobContent } from './PublicJobContent'
import type { Metadata } from 'next'

interface PageProps {
  params: {
    publicUrl: string
  }
}

// Generate structured data for job postings
function generateJobStructuredData(job: PublicJob) {
  const baseSalary = job.salary_min || job.salary_max ? {
    '@type': 'MonetaryAmount',
    currency: job.salary_currency || 'USD',
    ...(job.salary_min && job.salary_max ? {
      value: {
        '@type': 'QuantitativeValue',
        minValue: job.salary_min,
        maxValue: job.salary_max,
        unitText: 'YEAR'
      }
    } : job.salary_min ? {
      value: {
        '@type': 'QuantitativeValue',
        value: job.salary_min,
        unitText: 'YEAR'
      }
    } : {
      value: {
        '@type': 'QuantitativeValue',
        value: job.salary_max,
        unitText: 'YEAR'
      }
    })
  } : undefined

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    title: job.title,
    description: job.description,
    datePosted: job.created_at,
    validThrough: job.published_at ? new Date(new Date(job.published_at).getTime() + 365 * 24 * 60 * 60 * 1000).toISOString() : new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // Default to 1 year from published date or now
    employmentType: job.job_type.toUpperCase(),
    hiringOrganization: {
      '@type': 'Organization',
      name: job.organization_name || 'Company',
    },
    jobLocation: job.location ? {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: job.location,
      }
    } : undefined,
    baseSalary,
    experienceRequirements: {
      '@type': 'OccupationalExperienceRequirements',
      monthsOfExperience: getExperienceMonths(job.experience_level)
    },
    skills: job.skills_required?.join(', ') || '',
    occupationalCategory: job.department || '',
  }

  return JSON.stringify(structuredData)
}

function getExperienceMonths(experienceLevel: string): number {
  switch (experienceLevel.toLowerCase()) {
    case 'entry_level':
      return 0
    case 'junior':
      return 12 // 1 year
    case 'mid_level':
      return 36 // 3 years
    case 'senior':
      return 60 // 5 years
    case 'lead':
      return 96 // 8 years
    case 'executive':
      return 120 // 10 years
    default:
      return 0
  }
}

// Generate metadata for SEO
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const job = await apiClient.getPublicJob(params.publicUrl)

    const title = `${job.title} at ${job.organization_name || 'Our Company'}`
    const description = job.description.length > 160
      ? job.description.substring(0, 157) + '...'
      : job.description

    const canonicalUrl = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/jobs/${params.publicUrl}`

    return {
      title,
      description,
      keywords: [
        job.title,
        job.organization_name || '',
        job.department || '',
        job.location || '',
        'job',
        'career',
        'employment',
        'hiring'
      ].filter(Boolean),
      authors: [{ name: job.organization_name || 'Company' }],
      openGraph: {
        title,
        description,
        url: canonicalUrl,
        siteName: job.organization_name || 'ATS Platform',
        type: 'website',
        images: [
          {
            url: '/og-job-posting.png', // You can add a default OG image
            width: 1200,
            height: 630,
            alt: `${job.title} job posting`,
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title,
        description,
        images: ['/og-job-posting.png'],
      },
      alternates: {
        canonical: canonicalUrl,
      },
      robots: {
        index: true,
        follow: true,
        googleBot: {
          index: true,
          follow: true,
          'max-video-preview': -1,
          'max-image-preview': 'large',
          'max-snippet': -1,
        },
      },
    }
  } catch (error) {
    // Fallback metadata for error cases
    return {
      title: 'Job Not Found',
      description: 'The job posting you are looking for is not available.',
    }
  }
}

// Fetch job data on server side
async function getJobData(slug: string): Promise<PublicJob> {
  try {
    return await apiClient.getPublicJob(slug)
  } catch (error) {
    notFound()
  }
}

export default async function PublicJobPage({ params }: PageProps) {
  const job = await getJobData(params.publicUrl)
  const structuredData = generateJobStructuredData(job)

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: structuredData,
        }}
      />
      <PublicJobContent job={job} />
    </>
>>>>>>> origin/main
  )
}