import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReportsList } from '../ReportsList'
import { reportsApi } from '@/api/reports'

vi.mock('@/api/reports')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ReportsList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(reportsApi.list).mockImplementation(() => new Promise(() => {}))

    render(<ReportsList />, { wrapper: createWrapper() })

    expect(screen.getByText(/loading reports/i)).toBeInTheDocument()
  })

  it('should load and display reports', async () => {
    const mockReports = {
      reports: [
        {
          id: '1',
          name: 'Test Report',
          report_type: 'payroll_summary',
          format: 'pdf',
          status: 'completed',
          parameters: {},
          file_path: '/path/to/file.pdf',
          error_message: null,
          created_at: '2024-01-01T00:00:00Z',
          completed_at: '2024-01-01T00:05:00Z',
        },
      ],
    }
    vi.mocked(reportsApi.list).mockResolvedValue(mockReports)

    render(<ReportsList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument()
    })

    expect(screen.getByText('Payroll Summary')).toBeInTheDocument()
    expect(screen.getByText('PDF')).toBeInTheDocument()
  })

  it('should handle errors gracefully', async () => {
    vi.mocked(reportsApi.list).mockRejectedValue(new Error('API Error'))

    render(<ReportsList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/failed to load reports/i)).toBeInTheDocument()
    })
  })

  it('should filter reports by status', async () => {
    const mockReports = {
      reports: [
        {
          id: '1',
          name: 'Test Report',
          report_type: 'payroll_summary',
          format: 'pdf',
          status: 'completed',
          parameters: {},
          file_path: '/path/to/file.pdf',
          error_message: null,
          created_at: '2024-01-01T00:00:00Z',
          completed_at: '2024-01-01T00:05:00Z',
        },
        {
          id: '2',
          name: 'Pending Report',
          report_type: 'payroll_summary',
          format: 'pdf',
          status: 'pending',
          parameters: {},
          file_path: null,
          error_message: null,
          created_at: '2024-01-01T00:00:00Z',
          completed_at: null,
        },
      ],
    }
    vi.mocked(reportsApi.list).mockResolvedValue(mockReports)

    render(<ReportsList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument()
      expect(screen.getByText('Pending Report')).toBeInTheDocument()
    })
  })

  it('should display empty state when no reports', async () => {
    vi.mocked(reportsApi.list).mockResolvedValue({
      reports: [],
    })

    render(<ReportsList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/no reports found/i)).toBeInTheDocument()
    })
  })
})
