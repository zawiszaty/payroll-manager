import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AbsenceList } from '../AbsenceList'
import { absencesApi } from '@/api/absences'

vi.mock('@/api/absences')

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

describe('AbsenceList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(absencesApi.list).mockImplementation(() => new Promise(() => {}))

    render(<AbsenceList />, { wrapper: createWrapper() })

    expect(screen.getByText(/loading absences/i)).toBeInTheDocument()
  })

  it('should load and display absences', async () => {
    const mockAbsences = {
      items: [
        {
          id: '1',
          employee_id: 'emp-1',
          absence_type: 'vacation' as const,
          start_date: '2024-01-01',
          end_date: '2024-01-05',
          status: 'pending' as const,
          reason: 'Family vacation',
        },
      ],
      total: 1,
    }
    vi.mocked(absencesApi.list).mockResolvedValue(mockAbsences)

    render(<AbsenceList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Vacation')).toBeInTheDocument()
    })

    expect(screen.getByText('Pending')).toBeInTheDocument()
    expect(screen.getByText('Family vacation')).toBeInTheDocument()
  })

  it('should handle errors gracefully', async () => {
    vi.mocked(absencesApi.list).mockRejectedValue(new Error('API Error'))

    render(<AbsenceList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/failed to load absences/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no absences', async () => {
    vi.mocked(absencesApi.list).mockResolvedValue({
      items: [],
      total: 0,
    })

    render(<AbsenceList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/no absences found/i)).toBeInTheDocument()
    })
  })
})
