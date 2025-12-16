import type { UserResponse } from '@/api/models'
import { UserRole as ApiUserRole } from '@/api/models'

// Re-export the API UserRole to maintain compatibility
export { UserRole } from '@/api/models'

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: ApiUserRole
  employee_id?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthState {
  user: UserResponse | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
