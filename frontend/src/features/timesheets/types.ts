export enum TimesheetStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum OvertimeType {
  REGULAR = 'regular',
  WEEKEND = 'weekend',
  HOLIDAY = 'holiday',
  NIGHT_SHIFT = 'night_shift',
}

export interface Timesheet {
  id: string
  employee_id: string
  start_date: string
  end_date: string
  hours: number
  overtime_hours: number
  overtime_type: OvertimeType | null
  project_id: string | null
  task_description: string | null
  status: TimesheetStatus
  rejection_reason: string | null
  total_hours: number
  created_at: string
  updated_at: string
  submitted_at: string | null
  approved_at: string | null
  approved_by: string | null
}

export interface CreateTimesheetRequest {
  employee_id: string
  start_date: string
  end_date: string
  hours: number
  overtime_hours?: number
  overtime_type?: OvertimeType | null
  project_id?: string | null
  task_description?: string | null
}

export interface UpdateTimesheetRequest {
  hours: number
  overtime_hours?: number
  overtime_type?: OvertimeType | null
  project_id?: string | null
  task_description?: string | null
}

export interface ApproveTimesheetRequest {
  approved_by: string
}

export interface RejectTimesheetRequest {
  reason: string
}

export interface TimesheetListParams {
  skip?: number
  limit?: number
  status?: TimesheetStatus
  employee_id?: string
  start_date?: string
  end_date?: string
}

export interface TimesheetListResponse {
  items: Timesheet[]
  total: number
  skip: number
  limit: number
}

export interface HoursSummaryResponse {
  employee_id: string
  start_date: string
  end_date: string
  total_hours: number
}
