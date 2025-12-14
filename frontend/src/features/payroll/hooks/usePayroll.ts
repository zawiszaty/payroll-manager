import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import apiClient from '@/api/client'
import type {
  PayrollDetailView,
  PayrollListResponse,
  CreatePayrollRequest,
  CalculatePayrollRequest,
  ApprovePayrollRequest,
  MarkAsPaidRequest,
} from '../types'

const PAYROLL_KEYS = {
  all: ['payrolls'] as const,
  lists: () => [...PAYROLL_KEYS.all, 'list'] as const,
  list: (page: number, limit: number) => [...PAYROLL_KEYS.lists(), page, limit] as const,
  details: () => [...PAYROLL_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...PAYROLL_KEYS.details(), id] as const,
  byEmployee: (employeeId: string, page: number, limit: number) =>
    [...PAYROLL_KEYS.all, 'employee', employeeId, page, limit] as const,
}

// Fetch all payrolls with pagination
export function usePayrolls(page = 1, limit = 10) {
  return useQuery({
    queryKey: PAYROLL_KEYS.list(page, limit),
    queryFn: async () => {
      const response = await apiClient.get<PayrollListResponse>('/payrolls/', {
        params: { page, limit },
      })
      return response.data
    },
  })
}

// Fetch payrolls by employee
export function usePayrollsByEmployee(employeeId: string, page = 1, limit = 10) {
  return useQuery({
    queryKey: PAYROLL_KEYS.byEmployee(employeeId, page, limit),
    queryFn: async () => {
      const response = await apiClient.get<PayrollListResponse>(
        `/payrolls/employee/${employeeId}`,
        {
          params: { page, limit },
        }
      )
      return response.data
    },
    enabled: !!employeeId,
  })
}

// Fetch single payroll
export function usePayroll(id: string) {
  return useQuery({
    queryKey: PAYROLL_KEYS.detail(id),
    queryFn: async () => {
      const response = await apiClient.get<PayrollDetailView>(`/payrolls/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

// Create payroll
export function useCreatePayroll() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreatePayrollRequest) => {
      const response = await apiClient.post<PayrollDetailView>('/payrolls/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.lists() })
      toast.success('Payroll created successfully')
    },
    onError: (error: unknown) => {
      const detail = (
        error as {
          response?: { data?: { detail?: string | Array<{ loc: string[]; msg: string }> } }
        }
      ).response?.data?.detail
      let message = 'Failed to create payroll'

      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail.map((err) => `${err.loc.join('.')}: ${err.msg}`).join(', ')
      }

      toast.error(message)
      console.error('[Create Payroll Error]', error)
    },
  })
}

// Calculate payroll
export function useCalculatePayroll() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: CalculatePayrollRequest }) => {
      const response = await apiClient.post<PayrollDetailView>(`/payrolls/${id}/calculate`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.lists() })
      toast.success('Payroll calculated successfully')
    },
    onError: (error: unknown) => {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to calculate payroll')
      console.error('[Calculate Payroll Error]', error)
    },
  })
}

// Approve payroll
export function useApprovePayroll() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ApprovePayrollRequest }) => {
      const response = await apiClient.post<PayrollDetailView>(`/payrolls/${id}/approve`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.lists() })
      toast.success('Payroll approved successfully')
    },
    onError: (error: unknown) => {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to approve payroll')
      console.error('[Approve Payroll Error]', error)
    },
  })
}

// Process payroll
export function useProcessPayroll() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post<PayrollDetailView>(`/payrolls/${id}/process`)
      return response.data
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.detail(id) })
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.lists() })
      toast.success('Payroll processed successfully')
    },
    onError: (error: unknown) => {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to process payroll')
      console.error('[Process Payroll Error]', error)
    },
  })
}

// Mark payroll as paid
export function useMarkPayrollAsPaid() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: MarkAsPaidRequest }) => {
      const response = await apiClient.post<PayrollDetailView>(`/payrolls/${id}/mark-paid`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: PAYROLL_KEYS.lists() })
      toast.success('Payroll marked as paid successfully')
    },
    onError: (error: unknown) => {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
      toast.error(detail || 'Failed to mark payroll as paid')
      console.error('[Mark Payroll As Paid Error]', error)
    },
  })
}
