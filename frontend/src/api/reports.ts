import apiClient from './client'
import type { ReportListResponse, ReportResponse, CreateReportRequest } from '@/api'

export type { ReportResponse, CreateReportRequest } from '@/api'

export const reportsApi = {
  list: async (): Promise<ReportListResponse> => {
    const response = await apiClient.get<ReportListResponse>('/reporting/')
    return response.data
  },

  getById: async (id: string): Promise<ReportResponse> => {
    const response = await apiClient.get<ReportResponse>(`/reporting/${id}`)
    return response.data
  },

  create: async (data: CreateReportRequest): Promise<ReportResponse> => {
    const response = await apiClient.post<ReportResponse>('/reporting/', data)
    return response.data
  },

  getByStatus: async (status: string): Promise<ReportListResponse> => {
    const response = await apiClient.get<ReportListResponse>(`/reporting/status/${status}`)
    return response.data
  },

  getByType: async (type: string): Promise<ReportListResponse> => {
    const response = await apiClient.get<ReportListResponse>(`/reporting/type/${type}`)
    return response.data
  },

  download: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/reporting/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },
}
