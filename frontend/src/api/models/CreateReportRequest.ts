/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CreateReportRequest = {
  name: string
  report_type: string
  format: string
  employee_id?: string | null
  department?: string | null
  start_date?: string | null
  end_date?: string | null
  additional_filters?: Record<string, string> | null
}
