import apiClient from './client'
import type { AuditLogListResponse, AuditLogResponse } from '@/lib/api'

export type { AuditLogResponse } from '@/lib/api'

export const auditApi = {
  list: async (params?: {
    page?: number
    limit?: number
    entity_type?: string | null
    action?: string | null
  }): Promise<AuditLogListResponse> => {
    const response = await apiClient.get<AuditLogListResponse>('/audit/', {
      params: {
        page: params?.page || 1,
        limit: params?.limit || 100,
        entity_type: params?.entity_type,
        action: params?.action,
      },
    })
    return response.data
  },

  getById: async (id: string): Promise<AuditLogResponse> => {
    const response = await apiClient.get<AuditLogResponse>(`/audit/${id}`)
    return response.data
  },

  getByEntity: async (entityType: string, entityId: string): Promise<AuditLogResponse[]> => {
    const response = await apiClient.get<AuditLogListResponse>(
      `/audit/entity/${entityType}/${entityId}`
    )
    return response.data.items || []
  },

  getByEmployee: async (employeeId: string): Promise<AuditLogListResponse> => {
    const response = await apiClient.get<AuditLogListResponse>(`/audit/employee/${employeeId}`)
    return response.data
  },

  getTimeline: async (params?: {
    start_date?: string | null
    end_date?: string | null
    entity_type?: string | null
  }): Promise<AuditLogListResponse> => {
    const response = await apiClient.get<AuditLogListResponse>('/audit/timeline', {
      params: {
        start_date: params?.start_date,
        end_date: params?.end_date,
        entity_type: params?.entity_type,
      },
    })
    return response.data
  },
}
