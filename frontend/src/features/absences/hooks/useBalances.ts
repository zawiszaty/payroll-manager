import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { balancesApi } from '@/api/absences'
import type { CreateBalanceRequest, UpdateBalanceRequest } from '../types'

const BALANCES_QUERY_KEY = 'absence_balances'

export function useBalances(page: number = 1, limit: number = 100) {
  return useQuery({
    queryKey: [BALANCES_QUERY_KEY, page, limit],
    queryFn: () => balancesApi.list(page, limit),
  })
}

export function useBalance(id: string) {
  return useQuery({
    queryKey: [BALANCES_QUERY_KEY, id],
    queryFn: () => balancesApi.getById(id),
    enabled: !!id,
  })
}

export function useBalancesByEmployee(employeeId: string) {
  return useQuery({
    queryKey: [BALANCES_QUERY_KEY, 'employee', employeeId],
    queryFn: () => balancesApi.getByEmployee(employeeId),
    enabled: !!employeeId,
  })
}

export function useBalancesByEmployeeAndYear(employeeId: string, year: number) {
  return useQuery({
    queryKey: [BALANCES_QUERY_KEY, 'employee', employeeId, 'year', year],
    queryFn: () => balancesApi.getByEmployeeAndYear(employeeId, year),
    enabled: !!employeeId && !!year,
  })
}

export function useCreateBalance() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateBalanceRequest) => balancesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [BALANCES_QUERY_KEY] })
      toast.success('Balance created successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to create balance'
      toast.error(message)
    },
  })
}

export function useUpdateBalance() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateBalanceRequest }) =>
      balancesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [BALANCES_QUERY_KEY] })
      toast.success('Balance updated successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to update balance'
      toast.error(message)
    },
  })
}
