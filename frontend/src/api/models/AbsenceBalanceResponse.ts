/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceType } from './AbsenceType'
export type AbsenceBalanceResponse = {
  id: string
  employee_id: string
  absence_type: AbsenceType
  year: number
  total_days: string
  used_days: string
  remaining_days: string
}
