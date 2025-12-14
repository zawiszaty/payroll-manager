/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AuditLogResponse = {
  id: string
  entity_type: string
  entity_id: string
  employee_id: string | null
  action: string
  old_values: Record<string, any> | null
  new_values: Record<string, any> | null
  changed_by: string | null
  metadata: Record<string, any>
  occurred_at: string
  created_at: string
}
