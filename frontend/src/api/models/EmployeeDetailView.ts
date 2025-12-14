/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmploymentStatusView } from './EmploymentStatusView'
export type EmployeeDetailView = {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  date_of_birth: string | null
  hire_date: string | null
  statuses: Array<EmploymentStatusView>
  created_at: string | null
  updated_at: string | null
}
