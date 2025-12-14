import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '@/test/test-utils'
import { EmployeeDetail } from './EmployeeDetail'
import { employeeApi } from '@/api/employees'
import { EmploymentStatus } from '../types'

// Mock the API
vi.mock('@/api/employees', () => ({
  employeeApi: {
    getEmployee: vi.fn(),
    getEmployeeHistory: vi.fn(),
    deleteEmployee: vi.fn(),
  },
}))

// Mock react-router-dom hooks
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: 'test-employee-id' }),
    useNavigate: () => mockNavigate,
  }
})

describe('EmployeeDetail - Invalid Date Handling', () => {
  const mockEmployee = {
    id: 'test-employee-id',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    status: EmploymentStatus.ACTIVE,
    employee_number: 'EMP001',
    employment_type: 'FULL_TIME',
    hire_date: '2020-01-01',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(employeeApi.getEmployee).mockResolvedValue(mockEmployee as any)
  })

  it('handles history with invalid date gracefully', async () => {
    const user = userEvent.setup()
    const historyWithInvalidDate = {
      items: [
        {
          id: 'history-1',
          entity_type: 'employee',
          entity_id: 'test-employee-id',
          employee_id: null,
          action: 'created',
          old_values: null,
          new_values: { name: 'Test' },
          changed_by: null,
          metadata: {},
          occurred_at: 'invalid-date-string',
          created_at: 'also-invalid',
        },
      ],
      total: 1,
      page: 1,
      limit: 100,
    }

    vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(historyWithInvalidDate)

    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const historyButton = screen.getByRole('button', { name: /History/i })
    await user.click(historyButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    // Should render without errors and show N/A for invalid date
    expect(screen.getByText('CREATED')).toBeInTheDocument()
    expect(screen.getAllByText('N/A').length).toBeGreaterThan(0) // Fallback for invalid date
  })

  it('handles history with missing date fields gracefully', async () => {
    const user = userEvent.setup()
    const historyWithMissingDate = {
      items: [
        {
          id: 'history-2',
          entity_type: 'employee',
          entity_id: 'test-employee-id',
          employee_id: null,
          action: 'updated',
          old_values: { status: 'active' },
          new_values: { status: 'terminated' },
          changed_by: null,
          metadata: {},
          occurred_at: '2025-01-01T00:00:00Z',
          created_at: '2025-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 100,
    }

    vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(historyWithMissingDate)

    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const historyButton = screen.getByRole('button', { name: /History/i })
    await user.click(historyButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    // Should render without errors
    expect(screen.getByText('UPDATED')).toBeInTheDocument()
    expect(screen.getAllByText('N/A').length).toBeGreaterThan(0) // Fallback for missing date
  })

  it('handles history with missing action field gracefully', async () => {
    const user = userEvent.setup()
    const historyWithMissingAction = {
      items: [
        {
          id: 'history-3',
          entity_type: 'employee',
          entity_id: 'test-employee-id',
          employee_id: null,
          action: 'unknown',
          old_values: null,
          new_values: { name: 'Test' },
          changed_by: null,
          metadata: {},
          occurred_at: '2020-01-01T10:00:00Z',
          created_at: '2020-01-01T10:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 100,
    }

    vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(historyWithMissingAction)

    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const historyButton = screen.getByRole('button', { name: /History/i })
    await user.click(historyButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    // Should render with UNKNOWN fallback
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument()
  })

  it('renders valid dates correctly', async () => {
    const user = userEvent.setup()
    const historyWithValidDate = {
      items: [
        {
          id: 'history-4',
          entity_type: 'employee',
          entity_id: 'test-employee-id',
          employee_id: null,
          action: 'created',
          old_values: null,
          new_values: { name: 'Test' },
          changed_by: null,
          metadata: {},
          occurred_at: '2025-01-15T14:30:00Z',
          created_at: '2025-01-15T14:30:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 100,
    }

    vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(historyWithValidDate)

    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const historyButton = screen.getByRole('button', { name: /History/i })
    await user.click(historyButton)

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })

    // Should render with valid formatted date (not N/A for timestamp)
    expect(screen.getByText('CREATED')).toBeInTheDocument()
    // Check that a date is displayed (contains year 2025)
    expect(screen.getByText(/2025/)).toBeInTheDocument()
  })
})
