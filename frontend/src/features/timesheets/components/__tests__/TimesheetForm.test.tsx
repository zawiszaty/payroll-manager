import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '@/test/test-utils'
import { TimesheetForm } from '../TimesheetForm'
import { timesheetApi } from '@/api/timesheets'
import { OvertimeType } from '../../types'

vi.mock('@/api/timesheets', () => ({
  timesheetApi: {
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
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
    work_date: '2025-12-01',
    hours: 8,
    overtime_hours: 2,
    overtime_type: OvertimeType.REGULAR,
    project_id: 'project-1',
    task_description: 'Development work',
    status: 'draft' as const,
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
        expect(screen.getByText('Create Timesheet')).toBeInTheDocument()
        expect(screen.getByText('Add a new timesheet entry')).toBeInTheDocument()
      })
    })

    it('should render all form fields', async () => {
      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Employee ID')).toBeInTheDocument()
        expect(screen.getByLabelText('Work Date')).toBeInTheDocument()
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
        expect(screen.getByText('Create Timesheet')).toBeInTheDocument()
      })

      const submitButton = screen.getByText('Create Timesheet')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Employee ID is required')).toBeInTheDocument()
        expect(screen.getByText('Work date is required')).toBeInTheDocument()
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

      const submitButton = screen.getByText('Create Timesheet')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Hours cannot exceed 24')).toBeInTheDocument()
      })
    })

    it('should create timesheet on valid submission', async () => {
      const user = userEvent.setup()
      const newTimesheet = { ...mockTimesheet, id: 'new-timesheet' }
      vi.mocked(timesheetApi.create).mockResolvedValue(newTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        expect(screen.getByLabelText('Employee ID')).toBeInTheDocument()
      })

      await user.type(screen.getByLabelText('Employee ID'), 'employee-1')
      await user.type(screen.getByLabelText('Work Date'), '2025-12-01')
      await user.clear(screen.getByLabelText('Regular Hours'))
      await user.type(screen.getByLabelText('Regular Hours'), '8')
      await user.type(screen.getByLabelText('Task Description (Optional)'), 'Test work')

      const submitButton = screen.getByText('Create Timesheet')
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
        expect(screen.getByText('Edit Timesheet')).toBeInTheDocument()
        expect(screen.getByText('Update timesheet information')).toBeInTheDocument()
      })

      await waitFor(() => {
        const employeeInput = screen.getByLabelText('Employee ID') as HTMLInputElement
        expect(employeeInput.value).toBe('employee-1')
        expect(employeeInput.disabled).toBe(true)
      })
    })

    it('should disable employee_id and work_date in edit mode', async () => {
      vi.mocked(timesheetApi.getById).mockResolvedValue(mockTimesheet)

      render(<TimesheetForm />)

      await waitFor(() => {
        const employeeInput = screen.getByLabelText('Employee ID') as HTMLInputElement
        const dateInput = screen.getByLabelText('Work Date') as HTMLInputElement

        expect(employeeInput.disabled).toBe(true)
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
    it('should handle overtime type selection', async () => {
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
