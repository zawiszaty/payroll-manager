import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { TimesheetDetail } from '../TimesheetDetail'
import { timesheetApi } from '@/api/timesheets'
import { auditApi } from '@/api/audit'
import { TimesheetStatus, OvertimeType } from '../../types'

vi.mock('@/api/timesheets', () => ({
  timesheetApi: {
    getById: vi.fn(),
    delete: vi.fn(),
    submit: vi.fn(),
    approve: vi.fn(),
    reject: vi.fn(),
  },
}))

vi.mock('@/api/audit', () => ({
  auditApi: {
    getByEntity: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: 'timesheet-1' }),
    useNavigate: () => mockNavigate,
  }
})

describe('TimesheetDetail', () => {
  const mockDraftTimesheet = {
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

  const mockSubmittedTimesheet = {
    ...mockDraftTimesheet,
    status: TimesheetStatus.SUBMITTED,
    submitted_at: '2025-12-01T17:00:00Z',
  }

  const mockApprovedTimesheet = {
    ...mockDraftTimesheet,
    status: TimesheetStatus.APPROVED,
    submitted_at: '2025-12-01T17:00:00Z',
    approved_at: '2025-12-02T09:00:00Z',
    approved_by: 'manager-1',
  }

  const mockRejectedTimesheet = {
    ...mockDraftTimesheet,
    status: TimesheetStatus.REJECTED,
    submitted_at: '2025-12-01T17:00:00Z',
    rejection_reason: 'Incorrect hours',
  }

  const mockAuditLogs = [
    {
      id: 'audit-1',
      entity_type: 'timesheet',
      entity_id: 'timesheet-1',
      employee_id: 'employee-1',
      action: 'created',
      old_values: null,
      new_values: { hours: 8, status: 'draft' },
      changed_by: 'employee-1',
      metadata: {},
      occurred_at: '2025-12-01T09:00:00Z',
      created_at: '2025-12-01T09:00:00Z',
      event_type: 'Timesheet Created',
      timestamp: '2025-12-01T09:00:00Z',
      user_email: 'employee@example.com',
      event_data: {},
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(timesheetApi.getById).mockImplementation(() => new Promise(() => {}))

    render(<TimesheetDetail />)

    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('should render error state', async () => {
    vi.mocked(timesheetApi.getById).mockRejectedValue(new Error('Failed to fetch'))

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText(/failed to load timesheet details/i)).toBeInTheDocument()
    })
  })

  it('should display draft timesheet details', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Timesheet Details')).toBeInTheDocument()
      expect(screen.getByText('8h')).toBeInTheDocument()
      expect(screen.getByText('2h')).toBeInTheDocument()
      expect(screen.getByText('10h')).toBeInTheDocument()
      expect(screen.getAllByText('draft').length).toBeGreaterThan(0)
      expect(screen.getByText('Development work')).toBeInTheDocument()
    })
  })

  it('should show edit, submit, and delete buttons for draft timesheet', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Edit')).toBeInTheDocument()
      expect(screen.getByText('Submit')).toBeInTheDocument()
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })
  })

  it('should show approve and reject buttons for submitted timesheet', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockSubmittedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Approve')).toBeInTheDocument()
      expect(screen.getByText('Reject')).toBeInTheDocument()
    })
  })

  it('should not show action buttons for approved timesheet', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockApprovedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getAllByText('approved').length).toBeGreaterThan(0)
      expect(screen.queryByText('Edit')).not.toBeInTheDocument()
      expect(screen.queryByText('Submit')).not.toBeInTheDocument()
      expect(screen.queryByText('Approve')).not.toBeInTheDocument()
    })
  })

  it('should display approval information for approved timesheet', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockApprovedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Approved At')).toBeInTheDocument()
      expect(screen.getByText('Approved By')).toBeInTheDocument()
      expect(screen.getByText('manager-1')).toBeInTheDocument()
    })
  })

  it('should display rejection reason for rejected timesheet', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockRejectedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Rejection Reason')).toBeInTheDocument()
      expect(screen.getByText('Incorrect hours')).toBeInTheDocument()
    })
  })

  it('should not load audit logs on initial render', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Timesheet Details')).toBeInTheDocument()
    })

    expect(auditApi.getByEntity).not.toHaveBeenCalled()
  })

  it('should load audit logs when show history is clicked', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Show History')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(auditApi.getByEntity).toHaveBeenCalledWith('timesheet', 'timesheet-1')
    })
  })

  it('should toggle history button text', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockAuditLogs)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Show History')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(screen.getByText('Hide History')).toBeInTheDocument()
    })
  })

  it('should navigate to edit page on edit click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Edit')).toBeInTheDocument()
    })

    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)

    expect(mockNavigate).toHaveBeenCalledWith('/timesheets/timesheet-1/edit')
  })

  it('should navigate back to list on back button click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Timesheet Details')).toBeInTheDocument()
    })

    const backButtons = screen.getAllByRole('button')
    const backButton = backButtons.find((button) =>
      button.querySelector('svg')?.classList.contains('lucide-arrow-left')
    )

    if (backButton) {
      fireEvent.click(backButton)
      expect(mockNavigate).toHaveBeenCalledWith('/timesheets')
    }
  })

  it('should open delete dialog on delete click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText('Delete Timesheet')).toBeInTheDocument()
      expect(
        screen.getByText(/are you sure you want to delete this timesheet/i)
      ).toBeInTheDocument()
    })
  })

  it('should open submit dialog on submit click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Submit')).toBeInTheDocument()
    })

    const submitButton = screen.getByText('Submit')
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Submit Timesheet')).toBeInTheDocument()
      expect(
        screen.getByText(/you will not be able to edit it after submission/i)
      ).toBeInTheDocument()
    })
  })

  it('should open approve dialog on approve click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockSubmittedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Approve')).toBeInTheDocument()
    })

    const approveButton = screen.getByText('Approve')
    fireEvent.click(approveButton)

    await waitFor(() => {
      expect(screen.getByText('Approve Timesheet')).toBeInTheDocument()
      expect(screen.getByLabelText('Approver User ID')).toBeInTheDocument()
    })
  })

  it('should open reject dialog on reject click', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockSubmittedTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Reject')).toBeInTheDocument()
    })

    const rejectButton = screen.getByText('Reject')
    fireEvent.click(rejectButton)

    await waitFor(() => {
      expect(screen.getByText('Reject Timesheet')).toBeInTheDocument()
      expect(screen.getByLabelText('Rejection Reason')).toBeInTheDocument()
    })
  })

  it('should display overtime type in title case', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue(mockDraftTimesheet)

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('Regular')).toBeInTheDocument()
    })
  })

  it('should display "No project assigned" when project_id is null', async () => {
    vi.mocked(timesheetApi.getById).mockResolvedValue({
      ...mockDraftTimesheet,
      project_id: null,
    })

    render(<TimesheetDetail />)

    await waitFor(() => {
      expect(screen.getByText('No project assigned')).toBeInTheDocument()
    })
  })
})
