/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceType } from './AbsenceType'
export type AbsenceCreate = {
  employee_id: string
  absence_type: AbsenceType
  start_date: string
  end_date: string
  reason?: string | null
  notes?: string | null
}
