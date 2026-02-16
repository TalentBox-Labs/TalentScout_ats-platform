import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { JobShareSection } from '../components/JobShareSection'
import { vi } from 'vitest'

// Mock the ShareButton component
vi.mock('../components/ShareButton', () => ({
  ShareButton: ({ platform, url, text, onClick }: {
    platform: string;
    url: string;
    text: string;
    onClick?: () => void;
  }) => (
    <button
      data-testid={`share-button-${platform}`}
      onClick={onClick}
      aria-label={`Share on ${platform}`}
    >
      Share on {platform}
    </button>
  ),
}))

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Share2: () => <span data-testid="share-icon">📤</span>,
  Copy: () => <span data-testid="copy-icon">📋</span>,
  Check: () => <span data-testid="check-icon">✅</span>,
}))

describe('JobShareSection', () => {
  const defaultProps = {
    jobId: 'test-job-id',
    jobTitle: 'Senior Software Engineer',
  }

  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
  })

  it('renders share section with title', () => {
    render(<JobShareSection {...defaultProps} />)

    expect(screen.getByText('Share this job')).toBeInTheDocument()
    expect(screen.getByTestId('share-icon')).toBeInTheDocument()
  })

  it('renders all share buttons', () => {
    render(<JobShareSection {...defaultProps} />)

    expect(screen.getByTestId('share-button-linkedin')).toBeInTheDocument()
    expect(screen.getByTestId('share-button-twitter')).toBeInTheDocument()
    expect(screen.getByTestId('share-button-facebook')).toBeInTheDocument()
    expect(screen.getByTestId('share-button-email')).toBeInTheDocument()
    expect(screen.getByTestId('share-button-copy')).toBeInTheDocument()
  })

  it('displays job statistics', () => {
    render(<JobShareSection {...defaultProps} />)

    expect(screen.getByText('Share to attract top talent')).toBeInTheDocument()
  })

  it('handles share button clicks', async () => {
    // Mock window.open and console.error
    const mockOpen = vi.fn()
    const mockLog = vi.fn()
    global.window.open = mockOpen
    global.console.error = mockLog

    render(<JobShareSection {...defaultProps} />)

    const linkedinButton = screen.getByTestId('share-button-linkedin')

    fireEvent.click(linkedinButton)

    // Should attempt to open share URL
    await waitFor(() => {
      expect(mockOpen).toHaveBeenCalled()
    })

    // Should be called with LinkedIn share URL
    const calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('linkedin.com')
    expect(calledUrl).toContain('Senior%20Software%20Engineer')
  })

  it('handles copy link functionality', async () => {
    // Mock clipboard API
    const mockWriteText = vi.fn().mockResolvedValue(undefined)
    Object.assign(navigator, {
      clipboard: {
        writeText: mockWriteText,
      },
    })

    render(<JobShareSection {...defaultProps} />)

    const copyButton = screen.getByTestId('share-button-copy')

    fireEvent.click(copyButton)

    // Should copy link to clipboard
    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalled()
    })

    // Should show success feedback
    expect(screen.getByText('Link copied!')).toBeInTheDocument()
  })

  it('handles clipboard API errors gracefully', async () => {
    // Mock clipboard API to reject
    const mockWriteText = vi.fn().mockRejectedValue(new Error('Clipboard not available'))
    const mockLog = vi.fn()
    Object.assign(navigator, {
      clipboard: {
        writeText: mockWriteText,
      },
    })
    global.console.error = mockLog

    render(<JobShareSection {...defaultProps} />)

    const copyButton = screen.getByTestId('share-button-copy')

    fireEvent.click(copyButton)

    // Should handle error gracefully
    await waitFor(() => {
      expect(mockLog).toHaveBeenCalledWith('Failed to copy link:', expect.any(Error))
    })
  })

  it('falls back to prompt when clipboard API is not available', async () => {
    // Mock missing clipboard API
    const mockPrompt = vi.fn().mockReturnValue('copied-url')
    Object.assign(navigator, {
      clipboard: undefined,
    })
    global.window.prompt = mockPrompt

    render(<JobShareSection {...defaultProps} />)

    const copyButton = screen.getByTestId('share-button-copy')

    fireEvent.click(copyButton)

    // Should fall back to prompt
    await waitFor(() => {
      expect(mockPrompt).toHaveBeenCalled()
    })
  })

  it('generates correct share URLs for different platforms', () => {
    const mockOpen = vi.fn()
    global.window.open = mockOpen

    render(<JobShareSection {...defaultProps} />)

    // Test LinkedIn share
    const linkedinButton = screen.getByTestId('share-button-linkedin')
    fireEvent.click(linkedinButton)

    let calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('linkedin.com/sharing/share-offsite')
    expect(calledUrl).toContain('url=')
    expect(calledUrl).toContain('title=Senior%20Software%20Engineer')

    // Clear mock
    mockOpen.mockClear()

    // Test Twitter share
    const twitterButton = screen.getByTestId('share-button-twitter')
    fireEvent.click(twitterButton)

    calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('twitter.com/intent/tweet')
    expect(calledUrl).toContain('text=')
    expect(calledUrl).toContain('Senior%20Software%20Engineer')

    // Clear mock
    mockOpen.mockClear()

    // Test Facebook share
    const facebookButton = screen.getByTestId('share-button-facebook')
    fireEvent.click(facebookButton)

    calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('facebook.com/sharer/sharer.php')
    expect(calledUrl).toContain('u=')

    // Clear mock
    mockOpen.mockClear()

    // Test Email share
    const emailButton = screen.getByTestId('share-button-email')
    fireEvent.click(emailButton)

    calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('mailto:')
    expect(calledUrl).toContain('subject=')
    expect(calledUrl).toContain('body=')
  })

  it('handles share tracking errors gracefully', async () => {
    // Mock apiClient.trackShare to reject
    const mockTrackShare = vi.fn().mockRejectedValue(new Error('Tracking failed'))
    const mockLog = vi.fn()

    // We need to mock the apiClient import
    vi.doMock('../lib/api', () => ({
      apiClient: {
        trackShare: mockTrackShare,
      },
    }))

    global.console.error = mockLog

    render(<JobShareSection {...defaultProps} />)

    const linkedinButton = screen.getByTestId('share-button-linkedin')
    fireEvent.click(linkedinButton)

    // Should still attempt to open share URL even if tracking fails
    await waitFor(() => {
      expect(mockLog).toHaveBeenCalledWith('Failed to track share:', expect.any(Error))
    })
  })

  it('includes job URL in share links', () => {
    const mockOpen = vi.fn()
    global.window.open = mockOpen

    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: {
        origin: 'https://example.com',
      },
      writable: true,
    })

    render(<JobShareSection {...defaultProps} />)

    const linkedinButton = screen.getByTestId('share-button-linkedin')
    fireEvent.click(linkedinButton)

    const calledUrl = mockOpen.mock.calls[0][0]
    expect(calledUrl).toContain('https://example.com')
  })
})