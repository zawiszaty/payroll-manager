import apiClient from './client'
import type {
  Employee,
  CreateEmployeeRequest,
  UpdateEmployeeRequest,
  EmployeeListParams,
  EmployeeListResponse,
} from '@/features/employees/types'
import type { AuditLogListResponse } from './models/AuditLogListResponse'

/**
 * Employee API endpoints
 */
export const employeeApi = {
  /**
   * Get list of employees with optional filters
   */
  getEmployees: async (params?: EmployeeListParams): Promise<EmployeeListResponse> => {
    const response = await apiClient.get<EmployeeListResponse>('/employees', { params })
    return response.data
  },

  /**
   * Get a single employee by ID
   */
  getEmployee: async (id: string): Promise<Employee> => {
    const response = await apiClient.get<Employee>(`/employees/${id}`)
    return response.data
  },

  /**
   * Create a new employee
   */
  createEmployee: async (data: CreateEmployeeRequest): Promise<Employee> => {
    const response = await apiClient.post<Employee>('/employees', data)
    return response.data
  },

  /**
   * Update an existing employee
   */
  updateEmployee: async (id: string, data: UpdateEmployeeRequest): Promise<Employee> => {
    const response = await apiClient.put<Employee>(`/employees/${id}`, data)
    return response.data
  },

  /**
   * Delete an employee
   */
  deleteEmployee: async (id: string): Promise<void> => {
    await apiClient.delete(`/employees/${id}`)
  },

  /**
   * Get employee history/audit log
   */
  getEmployeeHistory: async (
    id: string,
    page: number = 1,
    limit: number = 100
  ): Promise<AuditLogListResponse> => {
    const response = await apiClient.get<AuditLogListResponse>(`/audit/employee/${id}`, {
      params: { page, limit },
    })
    return response.data
  },
}
