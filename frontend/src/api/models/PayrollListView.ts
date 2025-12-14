/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PayrollPeriodType } from './PayrollPeriodType'
import type { PayrollStatus } from './PayrollStatus'
/**
 * View for payroll list
 */
export type PayrollListView = {
  id: string
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  status: PayrollStatus
  gross_pay: string
  net_pay: string
  currency: string
  created_at: string | null
}
