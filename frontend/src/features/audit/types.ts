import type { AuditLogResponse } from '@/api/audit'

export type { AuditLogResponse }

export const ACTION_LABELS: Record<string, string> = {
  created: 'Created',
  updated: 'Updated',
  deleted: 'Deleted',
  approved: 'Approved',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
  activated: 'Activated',
  deactivated: 'Deactivated',
  status_changed: 'Status Changed',
}

export const ENTITY_TYPE_LABELS: Record<string, string> = {
  employee: 'Employee',
  contract: 'Contract',
  payroll: 'Payroll',
  timesheet: 'Timesheet',
  absence: 'Absence',
  compensation: 'Compensation',
  rate: 'Rate',
  bonus: 'Bonus',
}

export type AuditListParams = {
  page?: number
  limit?: number
  entity_type?: string | null
  action?: string | null
}

export type TimelineParams = {
  start_date?: string | null
  end_date?: string | null
  entity_type?: string | null
}
