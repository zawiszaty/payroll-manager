/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PayrollPeriodType } from './PayrollPeriodType'
export type CreatePayrollRequest = {
  employee_id: string
  period_type: PayrollPeriodType
  period_start_date: string
  period_end_date: string
  notes?: string | null
}
