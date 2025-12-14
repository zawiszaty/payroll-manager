import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { timesheetApi } from '@/api/timesheets'
import type {
  CreateTimesheetRequest,
  UpdateTimesheetRequest,
  ApproveTimesheetRequest,
  RejectTimesheetRequest,
} from '../types'

const TIMESHEETS_QUERY_KEY = 'timesheets'

export function useTimesheets() {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY],
    queryFn: () => timesheetApi.list(),
  })
}

export function useTimesheet(id: string) {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY, id],
    queryFn: () => timesheetApi.getById(id),
    enabled: !!id,
  })
}

export function useTimesheetsByEmployee(employeeId: string) {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY, 'employee', employeeId],
    queryFn: () => timesheetApi.getByEmployee(employeeId),
    enabled: !!employeeId,
  })
}

export function useTimesheetsByStatus(status: string) {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY, 'status', status],
    queryFn: () => timesheetApi.getByStatus(status),
    enabled: !!status,
  })
}

export function usePendingApprovalTimesheets() {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY, 'pending-approval'],
    queryFn: () => timesheetApi.getPendingApproval(),
  })
}

export function useHoursSummary(
  employeeId: string,
  startDate: string,
  endDate: string,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [TIMESHEETS_QUERY_KEY, 'hours-summary', employeeId, startDate, endDate],
    queryFn: () => timesheetApi.getHoursSummary(employeeId, startDate, endDate),
    enabled: enabled && !!employeeId && !!startDate && !!endDate,
  })
}

export function useCreateTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateTimesheetRequest) => timesheetApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      toast.success('Timesheet created successfully')
    },
    onError: (error: unknown) => {
      const detail = (
        error as {
          response?: { data?: { detail?: string | Array<{ loc: string[]; msg: string }> } }
        }
      ).response?.data?.detail
      let message = 'Failed to create timesheet'

      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail.map((err) => `${err.loc.join('.')}: ${err.msg}`).join(', ')
      }

      toast.error(message)
      console.error('[Create Timesheet Error]', error)
    },
  })
}

export function useUpdateTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTimesheetRequest }) =>
      timesheetApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY, variables.id] })
      toast.success('Timesheet updated successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to update timesheet'
      toast.error(message)
    },
  })
}

export function useSubmitTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => timesheetApi.submit(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY, id] })
      toast.success('Timesheet submitted successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to submit timesheet'
      toast.error(message)
    },
  })
}

export function useApproveTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ApproveTimesheetRequest }) =>
      timesheetApi.approve(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY, variables.id] })
      toast.success('Timesheet approved successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to approve timesheet'
      toast.error(message)
    },
  })
}

export function useRejectTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RejectTimesheetRequest }) =>
      timesheetApi.reject(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY, variables.id] })
      toast.success('Timesheet rejected')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to reject timesheet'
      toast.error(message)
    },
  })
}

export function useDeleteTimesheet() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => timesheetApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TIMESHEETS_QUERY_KEY] })
      toast.success('Timesheet deleted successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to delete timesheet'
      toast.error(message)
    },
  })
}
