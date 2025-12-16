import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '@/test/test-utils'
import { TimesheetForm } from '../TimesheetForm'
import { timesheetApi } from '@/api/timesheets'
import { OvertimeType, TimesheetStatus } from '../../types'

vi.mock('@/api/timesheets', () => ({
  timesheetApi: {
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}))

vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: 'employee-1',
            first_name: 'John',
            last_name: 'Doe',
            email: 'john@example.com',
          },
        ],
      },
    }),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
let mockParams: { id?: string } = {}

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => mockParams,
    useNavigate: () => mockNavigate,
  }
})

describe('TimesheetForm', () => {
  const mockTimesheet = {
    id: 'timesheet-1',
    employee_id: 'employee-1',
    start_date: '2025-12-01',
    end_date: '2025-12-01',
    hours: 8,
    overtime_hours: 2,
    overtime_type: OvertimeType.REGULAR,
    project_id: 'project-1',
    task_description: 'Development work',
    status: TimesheetStatus.DRAFT,
    rejection_reason: null,
    total_hours: 10,
    created_at: '2025-12-01T09:00:00Z',
    updated_at: '2025-12-01T09:00:00Z',
    submitted_at: null,
    approved_at: null,
    approved_by: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockParams = {}
  })

  describe('Create mode', () => {
    it('should render create form', async () => {
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Create Timesheet' })).toBeInTheDocument()
        expect(screen.getByText('Add a new timesheet entry')).toBeInTheDocument()
      })
    })

    it('should render all form fields', async () => {
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Employee')).toBeInTheDocument()
        expect(screen.getByLabelText('Start Date')).toBeInTheDocument()
        expect(screen.getByLabelText('End Date')).toBeInTheDocument()
        expect(screen.getByLabelText('Regular Hours')).toBeInTheDocument()
        expect(screen.getByLabelText('Overtime Hours')).toBeInTheDocument()
        expect(screen.getByLabelText('Project ID (Optional)')).toBeInTheDocument()
        expect(screen.getByLabelText('Task Description (Optional)')).toBeInTheDocument()
      })
    })

    it('should show overtime type field when overtime hours > 0', async () => {
      const user = userEvent.setup()
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Hours')).toBeInTheDocument()
      })

      const overtimeInput = screen.getByLabelText('Overtime Hours')
      await user.clear(overtimeInput)
      await user.type(overtimeInput, '2')

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Type')).toBeInTheDocument()
      })
    })

    it('should not show overtime type field when overtime hours is 0', async () => {
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Hours')).toBeInTheDocument()
      })

      expect(screen.queryByLabelText('Overtime Type')).not.toBeInTheDocument()
    })

    it('should validate required fields', async () => {
      const user = userEvent.setup()
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Create Timesheet' })).toBeInTheDocument()
      })

      const submitButton = screen.getByRole('button', { name: /Create Timesheet/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Employee ID is required')).toBeInTheDocument()
        expect(screen.getByText('Start date is required')).toBeInTheDocument()
      })
    })

    it('should validate hours range', async () => {
      const user = userEvent.setup()
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Regular Hours')).toBeInTheDocument()
      })

      const hoursInput = screen.getByLabelText('Regular Hours')
      await user.clear(hoursInput)
      await user.type(hoursInput, '25')

      const submitButton = screen.getByRole('button', { name: /Create Timesheet/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Hours cannot exceed 24')).toBeInTheDocument()
      })
    })

    it.skip('should create timesheet on valid submission', async () => {
      const user = userEvent.setup()
      const newTimesheet = { ...mockTimesheet, id: 'new-timesheet' }
      vi.mocked(timesheetApi.create).mockResolvedValue(newTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Employee')).toBeInTheDocument()
      })

      // Select employee
      const employeeSelect = screen.getByRole('combobox', { name: 'Employee' })
      await user.click(employeeSelect)
      await waitFor(() => {
        expect(screen.getByText(/John Doe/)).toBeInTheDocument()
      })
      await user.click(screen.getByText(/John Doe/))

      await user.type(screen.getByLabelText('Start Date'), '2025-12-01')
      await user.type(screen.getByLabelText('End Date'), '2025-12-01')
      await user.clear(screen.getByLabelText('Regular Hours'))
      await user.type(screen.getByLabelText('Regular Hours'), '8')
      await user.type(screen.getByLabelText('Task Description (Optional)'), 'Test work')

      const submitButton = screen.getByRole('button', { name: /Create Timesheet/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(timesheetApi.create).toHaveBeenCalled()
        expect(mockNavigate).toHaveBeenCalledWith('/timesheets/new-timesheet')
      })
    })

    it('should navigate to list on cancel', async () => {
      const user = userEvent.setup()
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByText('Cancel')).toBeInTheDocument()
      })

      const cancelButton = screen.getByText('Cancel')
      await user.click(cancelButton)

      expect(mockNavigate).toHaveBeenCalledWith('/timesheets')
    })
  })

  describe('Edit mode', () => {
    beforeEach(() => {
      mockParams = { id: 'timesheet-1' }
    })

    it('should render edit form with loading state', async () => {
      vi.mocked(timesheetApi.getById).mockImplementation(() => new Promise(() => {}))

      render(<TimesheetForm />)

      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })

    it('should load and display timesheet data', async () => {
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Edit Timesheet' })).toBeInTheDocument()
        expect(screen.getByText('Update timesheet information')).toBeInTheDocument()
      })

      await waitFor(() => {
        const employeeSelect = screen.getByRole('combobox', { name: 'Employee' })
        expect(employeeSelect).toBeDisabled()
      })
    })

    it('should disable employee_id and date fields in edit mode', async () => {
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        const employeeSelect = screen.getByRole('combobox', { name: 'Employee' })
        const dateInput = screen.getByLabelText('Start Date') as HTMLInputElement

        expect(employeeSelect).toBeDisabled()
        expect(dateInput.disabled).toBe(true)
      })
    })

    it('should update timesheet on valid submission', async () => {
      const user = userEvent.setup()
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)
      vi.mocked(timesheetApi.update).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByText('Edit Timesheet')).toBeInTheDocument()
      })

      await waitFor(() => {
        const hoursInput = screen.getByLabelText('Regular Hours')
        expect(hoursInput).toHaveValue(8)
      })

      const hoursInput = screen.getByLabelText('Regular Hours')
      await user.clear(hoursInput)
      await user.type(hoursInput, '7')

      const submitButton = screen.getByText('Update Timesheet')
      await user.click(submitButton)

      await waitFor(() => {
        expect(timesheetApi.update).toHaveBeenCalledWith(
          'timesheet-1',
          expect.objectContaining({
            hours: 7,
          })
        )
        expect(mockNavigate).toHaveBeenCalledWith('/timesheets/timesheet-1')
      })
    })

    it('should show overtime type when overtime hours are present', async () => {
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Type')).toBeInTheDocument()
      })
    })

    it('should show correct button text in edit mode', async () => {
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByText('Update Timesheet')).toBeInTheDocument()
      })
    })
  })

  describe('Overtime handling', () => {
    it.skip('should handle overtime type selection', async () => {
      const user = userEvent.setup()
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Hours')).toBeInTheDocument()
      })

      const overtimeInput = screen.getByLabelText('Overtime Hours')
      await user.clear(overtimeInput)
      await user.type(overtimeInput, '2')

      await waitFor(() => {
        expect(screen.getByLabelText('Overtime Type')).toBeInTheDocument()
      })

      const overtimeTypeSelect = screen.getByLabelText('Overtime Type')
      await user.click(overtimeTypeSelect)

      await waitFor(() => {
        expect(screen.getByText('Regular')).toBeInTheDocument()
        expect(screen.getByText('Weekend')).toBeInTheDocument()
        expect(screen.getByText('Holiday')).toBeInTheDocument()
        expect(screen.getByText('Night Shift')).toBeInTheDocument()
      })
    })
  })
})
