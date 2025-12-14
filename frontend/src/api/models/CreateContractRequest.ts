/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContractType } from './ContractType'
export type CreateContractRequest = {
  employee_id: string
  contract_type: ContractType
  rate_amount: number | string
  rate_currency?: string
  valid_from: string
  valid_to?: string | null
  hours_per_week?: number | null
  commission_percentage?: number | string | null
  description?: string | null
}
