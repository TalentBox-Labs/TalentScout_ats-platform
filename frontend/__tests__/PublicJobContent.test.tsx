import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { PublicJobContent } from '../app/jobs/[publicUrl]/PublicJobContent'
import { vi } from 'vitest'

// Mock the JobShareSection component
vi.mock('../../components/JobShareSection', () => ({
  JobShareSection: ({ jobId, jobTitle }: { jobId: string; jobTitle: string }) => (
    <div data-testid="job-share-section">
      Share {jobTitle} (ID: {jobId})
    </div>
  ),
}))

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  MapPin: () => <span data-testid="map-pin-icon">📍</span>,
  Clock: () => <span data-testid="clock-icon">🕒</span>,
  DollarSign: () => <span data-testid="dollar-icon">$</span>,
  Building: () => <span data-testid="building-icon">🏢</span>,
}))

// Mock UI components
vi.mock('../../components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div data-testid="card">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: { children: React.ReactNode }) => <h3 data-testid="card-title">{children}</h3>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div data-testid="card-content">{children}</div>,
}))

vi.mock('../../components/ui/badge', () => ({
  Badge: ({ children, variant }: { children: React.ReactNode; variant?: string }) => (
    <span data-testid={`badge-${variant || 'default'}`}>{children}</span>
  ),
}))

vi.mock('../../components/ui/button', () => ({
  Button: ({ children, onClick, size, variant }: {
    children: React.ReactNode;
    onClick?: () => void;
    size?: string;
    variant?: string
  }) => (
    <button
      data-testid={`button-${size || 'default'}-${variant || 'default'}`}
      onClick={onClick}
    >
      {children}
    </button>
  ),
}))

describe('PublicJobContent', () => {
  const mockJob = {
    id: 'test-job-id',
    title: 'Senior Software Engineer',
    description: 'We are looking for a senior software engineer...',
    requirements: '5+ years of experience...',
    responsibilities: 'Develop and maintain software...',
    department: 'Engineering',
    location: 'San Francisco, CA',
    job_type: 'full_time',
    experience_level: 'senior',
    salary_min: 120000,
    salary_max: 160000,
    salary_currency: 'USD',
    skills_required: ['React', 'TypeScript', 'Node.js'],
    organization_name: 'Tech Corp',
    created_at: '2024-01-15T10:00:00Z',
    view_count: 150,
    share_count: 25,
  }

  it('renders job title and organization', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
    expect(screen.getByText('Tech Corp')).toBeInTheDocument()
  })

  it('renders job metadata (location, date, badges)', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument()
    expect(screen.getByText('Posted 1/15/2024')).toBeInTheDocument()
    expect(screen.getByText('full time')).toBeInTheDocument()
    expect(screen.getByText('senior')).toBeInTheDocument()
    expect(screen.getByText('Engineering')).toBeInTheDocument()
  })

  it('renders salary information', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('$120,000 - $160,000')).toBeInTheDocument()
  })

  it('renders job share section', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByTestId('job-share-section')).toBeInTheDocument()
    expect(screen.getByText('Share Senior Software Engineer (ID: test-job-id)')).toBeInTheDocument()
  })

  it('renders job description', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Job Description')).toBeInTheDocument()
    expect(screen.getByText(mockJob.description)).toBeInTheDocument()
  })

  it('renders requirements when available', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Requirements')).toBeInTheDocument()
    expect(screen.getByText(mockJob.requirements)).toBeInTheDocument()
  })

  it('renders responsibilities when available', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Responsibilities')).toBeInTheDocument()
    expect(screen.getByText(mockJob.responsibilities)).toBeInTheDocument()
  })

  it('renders skills required', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Skills Required')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('Node.js')).toBeInTheDocument()
  })

  it('renders job statistics', () => {
    render(<PublicJobContent job={mockJob} />)

    expect(screen.getByText('Job Statistics')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument() // views
    expect(screen.getByText('25')).toBeInTheDocument() // shares
  })

  it('renders apply button', () => {
    render(<PublicJobContent job={mockJob} />)

    const applyButton = screen.getByText('Apply for this position')
    expect(applyButton).toBeInTheDocument()
  })

  it('handles missing optional fields gracefully', () => {
    const jobWithoutOptionals = {
      ...mockJob,
      department: undefined,
      location: undefined,
      salary_min: undefined,
      salary_max: undefined,
      requirements: undefined,
      responsibilities: undefined,
      skills_required: [],
    }

    render(<PublicJobContent job={jobWithoutOptionals} />)

    // Should not crash and should still render basic info
    expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
    expect(screen.getByText('Job Description')).toBeInTheDocument()

    // Should not render sections for missing data
    expect(screen.queryByText('Requirements')).not.toBeInTheDocument()
    expect(screen.queryByText('Responsibilities')).not.toBeInTheDocument()
    expect(screen.queryByText('Skills Required')).not.toBeInTheDocument()
  })

  it('formats salary correctly for different currencies', () => {
    const jobWithEuroSalary = {
      ...mockJob,
      salary_currency: 'EUR',
      salary_min: 50000,
      salary_max: 70000,
    }

    render(<PublicJobContent job={jobWithEuroSalary} />)

    expect(screen.getByText('€50,000 - €70,000')).toBeInTheDocument()
  })

  it('handles salary with only minimum value', () => {
    const jobWithMinSalary = {
      ...mockJob,
      salary_max: undefined,
    }

    render(<PublicJobContent job={jobWithMinSalary} />)

    expect(screen.getByText('$120,000+')).toBeInTheDocument()
  })

  it('handles salary with only maximum value', () => {
    const jobWithMaxSalary = {
      ...mockJob,
      salary_min: undefined,
      salary_max: 150000,
    }

    render(<PublicJobContent job={jobWithMaxSalary} />)

    expect(screen.getByText('Up to $150,000')).toBeInTheDocument()
  })
})