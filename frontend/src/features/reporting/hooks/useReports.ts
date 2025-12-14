import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { reportsApi } from '@/api/reports'
import type { CreateReportRequest } from '../types'

const REPORTS_QUERY_KEY = 'reports'

export function useReports() {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY],
    queryFn: () => reportsApi.list(),
  })
}

export function useReport(id: string) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, id],
    queryFn: () => reportsApi.getById(id),
    enabled: !!id,
  })
}

export function useReportsByStatus(status: string) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'status', status],
    queryFn: () => reportsApi.getByStatus(status),
    enabled: !!status,
  })
}

export function useReportsByType(type: string) {
  return useQuery({
    queryKey: [REPORTS_QUERY_KEY, 'type', type],
    queryFn: () => reportsApi.getByType(type),
    enabled: !!type,
  })
}

export function useCreateReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateReportRequest) => reportsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REPORTS_QUERY_KEY] })
      toast.success('Report generation started successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to create report'
      toast.error(message)
    },
  })
}

export function useDownloadReport() {
  return useMutation({
    mutationFn: async ({ id, name }: { id: string; name: string }) => {
      const blob = await reportsApi.download(id)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    onSuccess: () => {
      toast.success('Report downloaded successfully')
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Failed to download report'
      toast.error(message)
    },
  })
}
