export enum PayrollStatus {
  DRAFT = 'DRAFT',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  APPROVED = 'APPROVED',
  PROCESSED = 'PROCESSED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED',
}

export enum PayrollPeriodType {
  WEEKLY = 'WEEKLY',
  BIWEEKLY = 'BIWEEKLY',
  MONTHLY = 'MONTHLY',
}

export enum PayrollLineType {
  BASE_SALARY = 'BASE_SALARY',
  HOURLY_WAGE = 'HOURLY_WAGE',
  OVERTIME = 'OVERTIME',
  BONUS = 'BONUS',
  COMMISSION = 'COMMISSION',
  DEDUCTION = 'DEDUCTION',
  TAX = 'TAX',
  ABSENCE_DEDUCTION = 'ABSENCE_DEDUCTION',
}

export interface PayrollLine {
  line_type: PayrollLineType
  description: string
  quantity: number
  rate: number
  amount: number
  currency: string
  reference_id?: string
}

export interface PayrollListView {
  id: string
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  status: PayrollStatus
  gross_pay: number
  net_pay: number
  currency: string
  created_at?: string
}

export interface PayrollDetailView {
  id: string
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  status: PayrollStatus
  gross_pay: number
  total_deductions: number
  total_taxes: number
  net_pay: number
  currency: string
  lines: PayrollLine[]
  approved_by?: string
  approved_at?: string
  processed_at?: string
  paid_at?: string
  payment_reference?: string
  notes?: string
  version: string
  created_at?: string
  updated_at?: string
}

export interface CreatePayrollRequest {
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  notes?: string
}

export interface CalculatePayrollRequest {
  working_days?: number
}

export interface ApprovePayrollRequest {
  approved_by: string
}

export interface MarkAsPaidRequest {
  payment_reference: string
}

export interface PayrollListResponse {
  items: PayrollListView[]
  total: number
  page: number
  limit: number
  next?: string
  previous?: string
}
