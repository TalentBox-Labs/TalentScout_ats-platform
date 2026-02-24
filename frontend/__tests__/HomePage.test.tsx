import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/page'
import { vi } from 'vitest'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: vi.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock next/link
vi.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

describe('HomePage', () => {
  it('renders the main heading', () => {
    render(<HomePage />)
    const heading = screen.getByRole('heading', { name: /win the talent war/i })
    expect(heading).toBeInTheDocument()
  })

  it('renders the CTA buttons', () => {
    render(<HomePage />)
    const startTrialButton = screen.getByRole('link', { name: /start free trial/i })
    const signInButton = screen.getByRole('link', { name: /sign in/i })

    expect(startTrialButton).toBeInTheDocument()
    expect(signInButton).toBeInTheDocument()
  })

  it('renders statistics', () => {
    render(<HomePage />)
    const candidatesPlaced = screen.getByText('10K+')
    const activeRecruiters = screen.getByText('500+')
    const successRate = screen.getByText('95%')

    expect(candidatesPlaced).toBeInTheDocument()
    expect(activeRecruiters).toBeInTheDocument()
    expect(successRate).toBeInTheDocument()
  })
})