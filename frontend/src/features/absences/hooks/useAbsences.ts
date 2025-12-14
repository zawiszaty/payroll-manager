import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { absencesApi } from '@/api/absences'
import type { CreateAbsenceRequest } from '../types'

const ABSENCES_QUERY_KEY = 'absences'

export function useAbsences(page: number = 1, limit: number = 100) {
  return useQuery({
    queryKey: [ABSENCES_QUERY_KEY, page, limit],
    queryFn: () => absencesApi.list(page, limit),
  })
}

export function useAbsence(id: string) {
  return useQuery({
    queryKey: [ABSENCES_QUERY_KEY, id],
    queryFn: () => absencesApi.getById(id),
    enabled: !!id,
  })
}

export function useAbsencesByEmployee(employeeId: string) {
  return useQuery({
    queryKey: [ABSENCES_QUERY_KEY, 'employee', employeeId],
    queryFn: () => absencesApi.getByEmployee(employeeId),
    enabled: !!employeeId,
  })
}

export function useCreateAbsence() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateAbsenceRequest) => absencesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ABSENCES_QUERY_KEY] })
      toast.success('Absence created successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to create absence'
      toast.error(message)
    },
  })
}

export function useApproveAbsence() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => absencesApi.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ABSENCES_QUERY_KEY] })
      toast.success('Absence approved successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to approve absence'
      toast.error(message)
    },
  })
}

export function useRejectAbsence() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => absencesApi.reject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ABSENCES_QUERY_KEY] })
      toast.success('Absence rejected successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to reject absence'
      toast.error(message)
    },
  })
}

export function useCancelAbsence() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => absencesApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ABSENCES_QUERY_KEY] })
      toast.success('Absence cancelled successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to cancel absence'
      toast.error(message)
    },
  })
}
