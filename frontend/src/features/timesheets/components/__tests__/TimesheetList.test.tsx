import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { TimesheetList } from '../TimesheetList'
import { timesheetApi } from '@/api/timesheets'
import { TimesheetStatus, OvertimeType } from '../../types'

vi.mock('@/api/timesheets', () => ({
  timesheetApi: {
    list: vi.fn(),
    delete: vi.fn(),
    submit: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('TimesheetList', () => {
  const mockTimesheets = [
    {
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
    },
    {
      id: 'timesheet-2',
      employee_id: 'employee-2',
      start_date: '2025-12-02',
      end_date: '2025-12-02',
      hours: 8,
      overtime_hours: 0,
      overtime_type: null,
      project_id: null,
      task_description: 'Regular work',
      status: TimesheetStatus.SUBMITTED,
      rejection_reason: null,
      total_hours: 8,
      created_at: '2025-12-02T09:00:00Z',
      updated_at: '2025-12-02T09:00:00Z',
      submitted_at: '2025-12-02T17:00:00Z',
      approved_at: null,
      approved_by: null,
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(timesheetApi.list).mockImplementation(() => new Promise(() => {}))

    render(<TimesheetList />)

    expect(screen.getByText(/loading timesheets/i)).toBeInTheDocument()
  })

  it('should render error state', async () => {
    vi.mocked(timesheetApi.list).mockRejectedValue(new Error('Failed to fetch'))

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText(/failed to load timesheets/i)).toBeInTheDocument()
    })
  })

  it('should render empty state', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue([])

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText(/no timesheets found/i)).toBeInTheDocument()
    })
  })

  it('should load and display timesheets', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getAllByText('8h').length).toBeGreaterThan(0)
      expect(screen.getByText('10h')).toBeInTheDocument()
      expect(screen.getByText('draft')).toBeInTheDocument()
      expect(screen.getByText('submitted')).toBeInTheDocument()
    })
  })

  it('should display overtime hours with type', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('2h')).toBeInTheDocument()
      expect(screen.getByText('(regular)')).toBeInTheDocument()
    })
  })

  it('should navigate to create timesheet page', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue([])

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('Create Timesheet')).toBeInTheDocument()
    })

    const createButton = screen.getByText('Create Timesheet')
    fireEvent.click(createButton)

    expect(mockNavigate).toHaveBeenCalledWith('/timesheets/new')
  })

  it('should navigate to timesheet detail on view click', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const viewButtons = screen.getAllByTitle('View details')
    fireEvent.click(viewButtons[0])

    expect(mockNavigate).toHaveBeenCalledWith('/timesheets/timesheet-1')
  })

  it('should show edit button only for draft timesheets', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const editButtons = screen.queryAllByTitle('Edit')
    expect(editButtons).toHaveLength(1)
  })

  it('should show submit button only for draft timesheets', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const submitButtons = screen.queryAllByTitle('Submit for approval')
    expect(submitButtons).toHaveLength(1)
  })

  it('should show delete button only for draft timesheets', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const deleteButtons = screen.queryAllByTitle('Delete')
    expect(deleteButtons).toHaveLength(1)
  })

  it('should open delete dialog on delete click', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const deleteButton = screen.getByTitle('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText('Delete Timesheet')).toBeInTheDocument()
      expect(
        screen.getByText(/are you sure you want to delete this timesheet/i)
      ).toBeInTheDocument()
    })
  })

  it('should open submit dialog on submit click', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const submitButton = screen.getByTitle('Submit for approval')
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Submit Timesheet')).toBeInTheDocument()
      expect(
        screen.getByText(/you will not be able to edit it after submission/i)
      ).toBeInTheDocument()
    })
  })

  it('should cancel delete dialog', async () => {
    vi.mocked(timesheetApi.list).mockResolvedValue(mockTimesheets)

    render(<TimesheetList />)

    await waitFor(() => {
      expect(screen.getByText('draft')).toBeInTheDocument()
    })

    const deleteButton = screen.getByTitle('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText('Delete Timesheet')).toBeInTheDocument()
    })

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    await waitFor(() => {
      expect(screen.queryByText('Delete Timesheet')).not.toBeInTheDocument()
    })
  })
})
