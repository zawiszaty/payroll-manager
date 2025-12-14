/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContractStatus } from './ContractStatus'
import type { ContractType } from './ContractType'
export type ContractListView = {
  id: string
  employee_id: string
  contract_type: ContractType
  rate_amount: string
  rate_currency: string
  valid_from: string
  valid_to: string | null
  status: ContractStatus
  version: number
}
