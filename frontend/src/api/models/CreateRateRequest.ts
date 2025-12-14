/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RateType } from './RateType'
export type CreateRateRequest = {
  employee_id: string
  rate_type: RateType
  amount: number | string
  currency?: string
  valid_from: string
  valid_to?: string | null
  description?: string | null
}
