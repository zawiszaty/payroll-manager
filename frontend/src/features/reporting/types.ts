import type { ReportResponse, CreateReportRequest } from '@/api/reports'

export type { ReportResponse, CreateReportRequest }

export type ReportStatus = 'pending' | 'processing' | 'completed' | 'failed'

export type ReportType =
  | 'payroll_summary'
  | 'employee_compensation'
  | 'absence_summary'
  | 'timesheet_summary'
  | 'tax_report'
  | 'custom'

export type ReportFormat = 'pdf' | 'csv' | 'xlsx' | 'json'

export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  payroll_summary: 'Payroll Summary',
  employee_compensation: 'Employee Compensation',
  absence_summary: 'Absence Summary',
  timesheet_summary: 'Timesheet Summary',
  tax_report: 'Tax Report',
  custom: 'Custom Report',
}

export const REPORT_STATUS_LABELS: Record<ReportStatus, string> = {
  pending: 'Pending',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
}

export const REPORT_FORMAT_LABELS: Record<ReportFormat, string> = {
  pdf: 'PDF',
  csv: 'CSV',
  xlsx: 'Excel',
  json: 'JSON',
}
