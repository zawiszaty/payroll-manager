/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmploymentStatusType } from './EmploymentStatusType'
export type ChangeStatusRequest = {
  new_status: EmploymentStatusType
  effective_date: string
  reason?: string | null
}
