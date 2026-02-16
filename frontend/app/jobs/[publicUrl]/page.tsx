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
  )
}