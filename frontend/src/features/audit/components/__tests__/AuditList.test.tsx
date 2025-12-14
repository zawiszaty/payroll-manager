import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuditList } from '../AuditList'
import { auditApi } from '@/api/audit'

vi.mock('@/api/audit')

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

describe('AuditList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(auditApi.list).mockImplementation(() => new Promise(() => {}))

    render(<AuditList />, { wrapper: createWrapper() })

    expect(screen.getByText(/loading audit logs/i)).toBeInTheDocument()
  })

  it('should load and display audit logs', async () => {
    const mockAuditLogs = {
      items: [
        {
          id: '1',
          entity_type: 'employee',
          entity_id: 'emp-1',
          employee_id: 'emp-1',
          action: 'created',
          old_values: null,
          new_values: { name: 'John Doe' },
          changed_by: 'user-1',
          metadata: {},
          occurred_at: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 50,
    }
    vi.mocked(auditApi.list).mockResolvedValue(mockAuditLogs)

    render(<AuditList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Employee')).toBeInTheDocument()
    })

    expect(screen.getByText('Created')).toBeInTheDocument()
  })

  it('should handle errors gracefully', async () => {
    vi.mocked(auditApi.list).mockRejectedValue(new Error('API Error'))

    render(<AuditList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/failed to load audit logs/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no audit logs', async () => {
    vi.mocked(auditApi.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 50,
    })

    render(<AuditList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/no audit logs found/i)).toBeInTheDocument()
    })
  })

  it('should display multiple audit logs', async () => {
    const mockAuditLogs = {
      items: [
        {
          id: '1',
          entity_type: 'employee',
          entity_id: 'emp-1',
          employee_id: 'emp-1',
          action: 'created',
          old_values: null,
          new_values: {},
          changed_by: 'user-1',
          metadata: {},
          occurred_at: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: '2',
          entity_type: 'contract',
          entity_id: 'contract-1',
          employee_id: 'emp-1',
          action: 'updated',
          old_values: { status: 'draft' },
          new_values: { status: 'active' },
          changed_by: 'user-1',
          metadata: {},
          occurred_at: '2024-01-02T00:00:00Z',
          created_at: '2024-01-02T00:00:00Z',
        },
      ],
      total: 2,
      page: 1,
      limit: 50,
    }
    vi.mocked(auditApi.list).mockResolvedValue(mockAuditLogs)

    render(<AuditList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Employee')).toBeInTheDocument()
      expect(screen.getByText('Contract')).toBeInTheDocument()
    })
  })
})
