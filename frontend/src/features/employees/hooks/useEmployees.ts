import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { employeeApi } from '@/api/employees'
import type { EmployeeListParams, CreateEmployeeRequest, UpdateEmployeeRequest } from '../types'

const EMPLOYEES_QUERY_KEY = 'employees'

/**
 * Hook to fetch employees list
 */
export function useEmployees(params?: EmployeeListParams) {
  return useQuery({
    queryKey: [EMPLOYEES_QUERY_KEY, params],
    queryFn: () => employeeApi.getEmployees(params),
  })
}

/**
 * Hook to fetch a single employee
 */
export function useEmployee(id: string) {
  return useQuery({
    queryKey: [EMPLOYEES_QUERY_KEY, id],
    queryFn: () => employeeApi.getEmployee(id),
    enabled: !!id,
  })
}

/**
 * Hook to create a new employee
 */
export function useCreateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateEmployeeRequest) => employeeApi.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMPLOYEES_QUERY_KEY] })
      toast.success('Employee created successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to create employee'
      toast.error(message)
    },
  })
}

/**
 * Hook to update an employee
 */
export function useUpdateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateEmployeeRequest }) =>
      employeeApi.updateEmployee(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [EMPLOYEES_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [EMPLOYEES_QUERY_KEY, variables.id] })
      toast.success('Employee updated successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to update employee'
      toast.error(message)
    },
  })
}

/**
 * Hook to delete an employee
 */
export function useDeleteEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => employeeApi.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [EMPLOYEES_QUERY_KEY] })
      toast.success('Employee deleted successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to delete employee'
      toast.error(message)
    },
  })
}

/**
 * Hook to fetch employee history
 */
export function useEmployeeHistory(id: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [EMPLOYEES_QUERY_KEY, id, 'history'],
    queryFn: () => employeeApi.getEmployeeHistory(id),
    enabled: !!id && enabled,
  })
}
