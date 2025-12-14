/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PayrollLineView } from './PayrollLineView'
import type { PayrollPeriodType } from './PayrollPeriodType'
import type { PayrollStatus } from './PayrollStatus'
/**
 * View for payroll detail
 */
export type PayrollDetailView = {
  id: string
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  status: PayrollStatus
  gross_pay: string
  total_deductions: string
  total_taxes: string
  net_pay: string
  currency: string
  lines: Array<PayrollLineView>
  approved_by: string | null
  approved_at: string | null
  processed_at: string | null
  paid_at: string | null
  payment_reference: string | null
  notes: string | null
  version: string
  created_at: string | null
  updated_at: string | null
}
