/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContractStatus } from './ContractStatus'
import type { ContractTermsView } from './ContractTermsView'
export type ContractDetailView = {
  id: string
  employee_id: string
  terms: ContractTermsView
  status: ContractStatus
  version: number
  cancellation_reason: string | null
  canceled_at: string | null
  created_at: string | null
  updated_at: string | null
}
