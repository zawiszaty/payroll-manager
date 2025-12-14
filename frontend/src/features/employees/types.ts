export enum EmploymentStatus {
  ACTIVE = 'active',
  ON_LEAVE = 'on_leave',
  TERMINATED = 'terminated',
  SUSPENDED = 'suspended',
}

export enum EmploymentType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  CONTRACT = 'contract',
  TEMPORARY = 'temporary',
  INTERN = 'intern',
}

export interface Address {
  street: string
  city: string
  state: string
  postal_code: string
  country: string
}

export interface EmergencyContact {
  name: string
  relationship: string
  phone: string
  email?: string
}

export interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  date_of_birth: string
  personal_id?: string
  address?: Address
  emergency_contact?: EmergencyContact
  department?: string
  position?: string
  employment_type: EmploymentType
  hire_date: string
  termination_date?: string
  status: EmploymentStatus
  manager_id?: string
  notes?: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface CreateEmployeeRequest {
  first_name: string
  last_name: string
  email: string
  hire_date: string
  phone?: string
  date_of_birth?: string
}

export interface UpdateEmployeeRequest {
  first_name?: string
  last_name?: string
  email?: string
  phone?: string
  date_of_birth?: string
}

export interface EmployeeListParams {
  skip?: number
  limit?: number
  status?: EmploymentStatus
  employment_type?: EmploymentType
  department?: string
  search?: string
}

export interface EmployeeListResponse {
  items: Employee[]
  total: number
  skip: number
  limit: number
}
