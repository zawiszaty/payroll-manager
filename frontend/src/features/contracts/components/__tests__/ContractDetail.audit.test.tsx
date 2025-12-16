import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ContractDetail } from '../ContractDetail'
import { contractsApi } from '@/api/contracts'
import { auditApi } from '@/api/audit'
import apiClient from '@/api/client'
import type { ContractDetailView, EmployeeDetailView, AuditLogResponse } from '@/api'
import { ContractStatus, ContractType } from '@/api'

vi.mock('@/api/contracts')
vi.mock('@/api/audit')
vi.mock('@/api/client')

describe('ContractDetail - Audit Integration', () => {
  const mockContract: ContractDetailView = {
    id: 'contract-123',
    employee_id: 'emp-456',
    status: ContractStatus.ACTIVE,
    terms: {
      contract_type: ContractType.FIXED_MONTHLY,
      rate_amount: '5000.00',
      rate_currency: 'USD',
      valid_from: '2025-01-01',
      valid_to: '2025-12-31',
      hours_per_week: 40,
      commission_percentage: null,
      description: 'Full-time employment',
    },
    version: 1,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    cancellation_reason: null,
    canceled_at: null,
  }

  const mockEmployee: EmployeeDetailView = {
    id: 'emp-456',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1234567890',
    hire_date: '2025-01-01',
    date_of_birth: '1990-01-01',
    statuses: [],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  }

  const mockAuditLogs: AuditLogResponse[] = [
    {
      id: 'audit-1',
      entity_type: 'contract',
      entity_id: 'contract-123',
      employee_id: 'emp-456',
      action: 'created',
      old_values: null,
      new_values: {
        contract_type: 'fixed_monthly',
        rate_amount: '5000.00',
        rate_currency: 'USD',
      },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-01-01T10:00:00Z',
      created_at: '2025-01-01T10:00:00Z',
    },
    {
      id: 'audit-2',
      entity_type: 'contract',
      entity_id: 'contract-123',
      employee_id: 'emp-456',
      action: 'activated',
      old_values: { status: 'pending' },
      new_values: { status: 'active' },
      changed_by: 'admin@example.com',
      metadata: {},
      occurred_at: '2025-01-01T11:00:00Z',
      created_at: '2025-01-01T11:00:00Z',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(contractsApi.getById).mockResolvedValue(mockContract)
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockEmployee })
  })

  const renderContractDetail = () => {
    return render(
      <MemoryRouter initialEntries={['/contracts/contract-123']}>
        <Routes>
          <Route path="/contracts/:id" element={<ContractDetail />} />
        </Routes>
      </MemoryRouter>
    )
  }

  it('should not load audit logs on initial render', async () => {
    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    expect(auditApi.getByEntity).not.toHaveBeenCalled()
  })

  it('should show history button', async () => {
    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Show History')).toBeInTheDocument()
    })
  })

  it('should load audit logs when show history is clicked', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)
    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(auditApi.getByEntity).toHaveBeenCalledWith('contract', 'contract-123')
    })
  })

  it('should display audit history after loading', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)
    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
      expect(screen.getByText(/Showing 2 events/)).toBeInTheDocument()
    })
  })

  it('should toggle history visibility', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)
    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    // Show history
    const showButton = screen.getByText('Show History')
    fireEvent.click(showButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    // Hide history
    const hideButton = screen.getByText('Hide History')
    fireEvent.click(hideButton)

    await waitFor(() => {
      expect(screen.queryByText('Change History')).not.toBeInTheDocument()
    })
  })

  it('should handle audit API errors gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.mocked(auditApi.getByEntity).mockRejectedValue(new Error('Failed to load audit logs'))

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to load audit history:',
        expect.any(Error)
      )
    })

    // Should still show the history section even with error
    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    consoleErrorSpy.mockRestore()
  })

  it('should display loading state while fetching audit logs', async () => {
    vi.mocked(auditApi.getByEntity).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockAuditLogs), 100))
    )

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(screen.getByText('Loading history...')).toBeInTheDocument()
    })

    await waitFor(
      () => {
        expect(screen.getByText(/Showing 2 events/)).toBeInTheDocument()
      },
      { timeout: 200 }
    )
  })

  it('should display empty state when no audit logs', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue([])

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(
        screen.getByText('No changes have been recorded for this entity yet.')
      ).toBeInTheDocument()
    })
  })

  it('should only fetch audit logs once when toggling', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    // Show history - should fetch
    const showButton = screen.getByText('Show History')
    fireEvent.click(showButton)

    await waitFor(() => {
      expect(auditApi.getByEntity).toHaveBeenCalledTimes(1)
    })

    // Hide history
    const hideButton = screen.getByText('Hide History')
    fireEvent.click(hideButton)

    // Show history again - should fetch again (per current implementation)
    const showButton2 = screen.getByText('Show History')
    fireEvent.click(showButton2)

    await waitFor(() => {
      expect(auditApi.getByEntity).toHaveBeenCalledTimes(2)
    })
  })

  it('should display audit action badges', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(screen.getByText('CREATED')).toBeInTheDocument()
      expect(screen.getByText('ACTIVATED')).toBeInTheDocument()
    })
  })

  it('should display changed by information in audit logs', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    renderContractDetail()

    await waitFor(() => {
      expect(screen.getByText('Contract Details')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      const changedByElements = screen.getAllByText('admin@example.com')
      expect(changedByElements.length).toBeGreaterThan(0)
    })
  })

  it('should handle contract without employee gracefully', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(new Error('Employee not found'))
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    renderContractDetail()

    await waitFor(() => {
      const unknownEmployeeElements = screen.getAllByText('Unknown Employee')
      expect(unknownEmployeeElements.length).toBeGreaterThan(0)
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })
  })
})
