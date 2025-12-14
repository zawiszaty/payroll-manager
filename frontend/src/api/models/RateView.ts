/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RateType } from './RateType'
export type RateView = {
  id: string
  employee_id: string
  rate_type: RateType
  amount: string
  currency: string
  valid_from: string
  valid_to: string | null
  description: string | null
  created_at: string | null
  updated_at: string | null
}
