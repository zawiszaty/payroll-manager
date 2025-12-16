/**
 * Application-wide constants
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Storage Keys
export const TOKEN_STORAGE_KEY = 'payroll_token'
export const REFRESH_TOKEN_STORAGE_KEY = 'payroll_refresh_token'
export const USER_STORAGE_KEY = 'payroll_user'

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

// Date Formats
export const DATE_FORMAT = 'yyyy-MM-dd'
export const DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'
export const DISPLAY_DATE_FORMAT = 'MMM dd, yyyy'
export const DISPLAY_DATETIME_FORMAT = 'MMM dd, yyyy HH:mm'

// Currency
export const DEFAULT_CURRENCY = 'USD'
export const SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'PLN'] as const

// Employment Status Types
export const EMPLOYMENT_STATUSES = {
  ACTIVE: 'active',
  ON_LEAVE: 'on_leave',
  TERMINATED: 'terminated',
  SUSPENDED: 'suspended',
} as const

// Contract Types
export const CONTRACT_TYPES = {
  FIXED_MONTHLY: 'fixed_monthly',
  HOURLY: 'hourly',
  B2B_DAILY: 'b2b_daily',
  B2B_HOURLY: 'b2b_hourly',
  TASK_BASED: 'task_based',
  COMMISSION_BASED: 'commission_based',
} as const

// Contract Status
export const CONTRACT_STATUSES = {
  PENDING: 'pending',
  ACTIVE: 'active',
  EXPIRED: 'expired',
  CANCELED: 'canceled',
} as const

// Absence Types
export const ABSENCE_TYPES = {
  VACATION: 'vacation',
  SICK_LEAVE: 'sick_leave',
  PARENTAL_LEAVE: 'parental_leave',
  UNPAID_LEAVE: 'unpaid_leave',
  BEREAVEMENT: 'bereavement',
  STUDY_LEAVE: 'study_leave',
  COMPASSIONATE: 'compassionate',
} as const

// Absence Status
export const ABSENCE_STATUSES = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CANCELLED: 'cancelled',
} as const

// Timesheet Status
export const TIMESHEET_STATUSES = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
} as const

// Overtime Types
export const OVERTIME_TYPES = {
  REGULAR: 'regular',
  WEEKEND: 'weekend',
  HOLIDAY: 'holiday',
  NIGHT_SHIFT: 'night_shift',
} as const

// Payroll Status
export const PAYROLL_STATUSES = {
  DRAFT: 'DRAFT',
  PENDING_APPROVAL: 'PENDING_APPROVAL',
  APPROVED: 'APPROVED',
  PROCESSED: 'PROCESSED',
  PAID: 'PAID',
  CANCELLED: 'CANCELLED',
} as const

// Report Types
export const REPORT_TYPES = {
  PAYROLL_SUMMARY: 'payroll_summary',
  EMPLOYEE_COMPENSATION: 'employee_compensation',
  ABSENCE_SUMMARY: 'absence_summary',
  TIMESHEET_SUMMARY: 'timesheet_summary',
  TAX_REPORT: 'tax_report',
  CUSTOM: 'custom',
} as const

// Report Formats
export const REPORT_FORMATS = {
  PDF: 'pdf',
  CSV: 'csv',
  XLSX: 'xlsx',
  JSON: 'json',
} as const

// Report Status
export const REPORT_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

// User Roles
export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  VIEWER: 'viewer',
} as const

// User Status
export const USER_STATUSES = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
} as const

// Rate Types
export const RATE_TYPES = {
  BASE_SALARY: 'base_salary',
  HOURLY_RATE: 'hourly_rate',
  DAILY_RATE: 'daily_rate',
} as const

// Bonus Types
export const BONUS_TYPES = {
  PERFORMANCE: 'performance',
  ANNUAL: 'annual',
  SIGNING: 'signing',
  RETENTION: 'retention',
  PROJECT: 'project',
  HOLIDAY: 'holiday',
} as const

// Entity Types (for audit)
export const ENTITY_TYPES = {
  EMPLOYEE: 'employee',
  CONTRACT: 'contract',
  PAYROLL: 'payroll',
  ABSENCE: 'absence',
  ABSENCE_BALANCE: 'absence_balance',
  RATE: 'rate',
  BONUS: 'bonus',
  DEDUCTION: 'deduction',
  OVERTIME: 'overtime',
  SICK_LEAVE: 'sick_leave',
  REPORT: 'report',
  TIMESHEET: 'timesheet',
} as const

// Audit Actions
export const AUDIT_ACTIONS = {
  CREATED: 'created',
  UPDATED: 'updated',
  DELETED: 'deleted',
  STATUS_CHANGED: 'status_changed',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CANCELED: 'canceled',
  ACTIVATED: 'activated',
  EXPIRED: 'expired',
  CALCULATED: 'calculated',
  PROCESSED: 'processed',
  PAID: 'paid',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const
