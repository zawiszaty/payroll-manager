/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BonusType } from './BonusType'
export type CreateBonusRequest = {
  employee_id: string
  bonus_type: BonusType
  amount: number | string
  currency?: string
  payment_date: string
  description?: string | null
}
