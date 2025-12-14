/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContractType } from './ContractType'
export type ContractTermsView = {
  contract_type: ContractType
  rate_amount: string
  rate_currency: string
  valid_from: string
  valid_to: string | null
  hours_per_week: number | null
  commission_percentage: string | null
  description: string | null
}
