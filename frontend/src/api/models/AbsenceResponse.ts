/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceStatus } from './AbsenceStatus'
import type { AbsenceType } from './AbsenceType'
export type AbsenceResponse = {
  id: string
  employee_id: string
  absence_type: AbsenceType
  start_date: string
  end_date: string
  status: AbsenceStatus
  reason?: string | null
  notes?: string | null
}
