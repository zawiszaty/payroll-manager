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

describe('EmployeeDetail', () => {
  const mockEmployee = {
    id: 'test-employee-id',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1234567890',
    date_of_birth: '1990-01-15',
    personal_id: 'ID123456',
    employee_number: 'EMP001',
    employment_type: 'FULL_TIME',
    position: 'Software Engineer',
    department: 'Engineering',
    hire_date: '2020-01-01',
    status: EmploymentStatus.ACTIVE,
    address: {
      street: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      postal_code: '94102',
      country: 'USA',
    },
    emergency_contact: {
      name: 'Jane Doe',
      relationship: 'Spouse',
      phone: '+1234567891',
    },
  }

  const mockHistory = {
    items: [
      {
        id: 'history-1',
        entity_type: 'employee',
        entity_id: 'test-employee-id',
        employee_id: 'test-employee-id',
        action: 'created',
        old_values: null,
        new_values: {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
        },
        changed_by: 'admin-user-id',
        metadata: {
          source_event: 'EmployeeCreatedEvent',
        },
        occurred_at: '2020-01-01T10:00:00Z',
        created_at: '2020-01-01T10:00:00Z',
        event_type: 'Employee Created',
        timestamp: '2020-01-01T10:00:00Z',
        user_email: 'admin@example.com',
        event_data: {
          first_name: 'John',
          last_name: 'Doe',
        },
      },
      {
        id: 'history-2',
        entity_type: 'employee',
        entity_id: 'test-employee-id',
        employee_id: 'test-employee-id',
        action: 'updated',
        old_values: {
          position: 'Junior Software Engineer',
        },
        new_values: {
          position: 'Software Engineer',
        },
        changed_by: 'admin-user-id',
        metadata: {
          source_event: 'EmployeeUpdatedEvent',
        },
        occurred_at: '2021-06-01T14:30:00Z',
        created_at: '2021-06-01T14:30:00Z',
        event_type: 'Employee Updated',
        timestamp: '2021-06-01T14:30:00Z',
        user_email: 'hr@example.com',
        event_data: {
          field: 'position',
          old_value: 'Junior Software Engineer',
          new_value: 'Software Engineer',
        },
      },
    ],
    total: 2,
    page: 1,
    limit: 100,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(employeeApi.getEmployee).mockResolvedValue(mockEmployee as any)
    vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(mockHistory)
  })

  it('renders employee details without errors', async () => {
    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getAllByText('john.doe@example.com')[0]).toBeInTheDocument()
    expect(screen.getByText('Personal Information')).toBeInTheDocument()
    expect(screen.getByText('Employment Information')).toBeInTheDocument()
  })

  it('displays loading state initially', () => {
    vi.mocked(employeeApi.getEmployee).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<EmployeeDetail />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays error state when employee fetch fails', async () => {
    vi.mocked(employeeApi.getEmployee).mockRejectedValue(new Error('Failed to fetch'))

    render(<EmployeeDetail />)

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument()
      expect(screen.getByText('Failed to load employee details')).toBeInTheDocument()
    })
  })

  describe('History View', () => {
    it('does not show history initially', async () => {
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      expect(screen.queryByText('Change History')).not.toBeInTheDocument()
    })

    it('shows history when History button is clicked', async () => {
      const user = userEvent.setup()
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })
      await user.click(historyButton)

      await waitFor(() => {
        expect(screen.getByText('Change History')).toBeInTheDocument()
      })
    })

    it('renders history items correctly without errors', async () => {
      const user = userEvent.setup()
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })
      await user.click(historyButton)

      await waitFor(() => {
        expect(screen.getByText('Change History')).toBeInTheDocument()
      })

      // Check that history items are rendered with actions
      expect(screen.getByText('CREATED')).toBeInTheDocument()
      expect(screen.getByText('UPDATED')).toBeInTheDocument()

      // Check that entity types are shown
      expect(screen.getAllByText(/Entity: employee/i).length).toBe(2)

      // Check that values are displayed
      expect(screen.getAllByText('New Values:').length).toBeGreaterThan(0)

      // Check total count
      expect(screen.getByText(/Showing 2 of 2 events/)).toBeInTheDocument()
    })

    it('shows loading state while fetching history', async () => {
      const user = userEvent.setup()
      vi.mocked(employeeApi.getEmployeeHistory).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })
      await user.click(historyButton)

      await waitFor(() => {
        expect(screen.getByText('Loading history...')).toBeInTheDocument()
      })
    })

    it('shows message when no history is available', async () => {
      const user = userEvent.setup()
      vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        limit: 100,
      })

      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })
      await user.click(historyButton)

      await waitFor(() => {
        expect(screen.getByText('No history available')).toBeInTheDocument()
      })
    })

    it('handles history with null/undefined values gracefully', async () => {
      const user = userEvent.setup()
      const historyWithNullData = {
        items: [
          {
            id: 'history-3',
            entity_type: 'employee',
            entity_id: 'test-employee-id',
            employee_id: 'test-employee-id',
            action: 'created',
            old_values: null,
            new_values: null,
            changed_by: 'admin-user-id',
            metadata: {},
            occurred_at: '2020-01-01T10:00:00Z',
            created_at: '2020-01-01T10:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        limit: 100,
      }

      vi.mocked(employeeApi.getEmployeeHistory).mockResolvedValue(historyWithNullData)

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
      expect(screen.getByText('CREATED')).toBeInTheDocument()
      expect(screen.getByText(/Entity: employee/i)).toBeInTheDocument()
    })

    it('toggles history visibility on multiple clicks', async () => {
      const user = userEvent.setup()
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })

      // Show history
      await user.click(historyButton)
      await waitFor(() => {
        expect(screen.getByText('Change History')).toBeInTheDocument()
      })

      // Hide history
      await user.click(historyButton)
      await waitFor(() => {
        expect(screen.queryByText('Change History')).not.toBeInTheDocument()
      })

      // Show again
      await user.click(historyButton)
      await waitFor(() => {
        expect(screen.getByText('Change History')).toBeInTheDocument()
      })
    })

    it('renders event timestamps correctly', async () => {
      const user = userEvent.setup()
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const historyButton = screen.getByRole('button', { name: /History/i })
      await user.click(historyButton)

      await waitFor(() => {
        expect(screen.getByText('Change History')).toBeInTheDocument()
      })

      // Check that timestamps are formatted (date-fns format: 'PPp')
      // The exact format depends on locale, but it should contain date and time
      const timestamps = screen.getAllByText(/Jan|Jun|2020|2021/)
      expect(timestamps.length).toBeGreaterThan(0)
    })
  })

  describe('Employee Information Display', () => {
    it('renders all personal information fields', async () => {
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      expect(screen.getByText('First Name')).toBeInTheDocument()
      expect(screen.getByText('Last Name')).toBeInTheDocument()
      expect(screen.getByText('Email')).toBeInTheDocument()
      expect(screen.getByText('Phone')).toBeInTheDocument()
      expect(screen.getByText('Date of Birth')).toBeInTheDocument()
      expect(screen.getByText('Personal ID')).toBeInTheDocument()
      expect(screen.getByText('Address')).toBeInTheDocument()
      expect(screen.getByText('Emergency Contact')).toBeInTheDocument()
    })

    it('renders all employment information fields', async () => {
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      expect(screen.getByText('Employee Number')).toBeInTheDocument()
      expect(screen.getByText('Employment Type')).toBeInTheDocument()
      expect(screen.getByText('Position')).toBeInTheDocument()
      expect(screen.getByText('Department')).toBeInTheDocument()
      expect(screen.getByText('Hire Date')).toBeInTheDocument()
      expect(screen.getByText(/Status/)).toBeInTheDocument()
    })

    it('displays ACTIVE status badge correctly', async () => {
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const badges = screen.getAllByText(/active/i)
      expect(badges.length).toBeGreaterThan(0)
    })
  })

  describe('Action Buttons', () => {
    it('renders all action buttons', async () => {
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      expect(screen.getByRole('button', { name: /History/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Edit/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Delete/i })).toBeInTheDocument()
    })

    it('navigates back when back button is clicked', async () => {
      const user = userEvent.setup()
      render(<EmployeeDetail />)

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })

      const backButton = screen.getAllByRole('button')[0] // First button is back
      await user.click(backButton)

      expect(mockNavigate).toHaveBeenCalledWith('/employees')
    })
  })
})
