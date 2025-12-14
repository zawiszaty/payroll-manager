/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PayrollLineType } from './PayrollLineType'
/**
 * View for payroll line items
 */
export type PayrollLineView = {
  line_type: PayrollLineType
  description: string
  quantity: string
  rate: string
  amount: string
  currency: string
  reference_id: string | null
}
