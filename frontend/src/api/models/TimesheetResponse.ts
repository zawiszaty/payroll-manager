/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TimesheetResponse = {
  id: string
  employee_id: string
  start_date: string
  end_date: string
  hours: number
  overtime_hours: number
  overtime_type: string | null
  project_id: string | null
  task_description: string | null
  status: string
  rejection_reason: string | null
  total_hours: number
  created_at: string
  updated_at: string
  submitted_at: string | null
  approved_at: string | null
  approved_by: string | null
}
