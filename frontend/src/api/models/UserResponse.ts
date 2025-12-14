/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole'
import type { UserStatus } from './UserStatus'
export type UserResponse = {
  id: string
  email: string
  role: UserRole
  status: UserStatus
  full_name: string | null
  created_at: string
  updated_at: string
}
