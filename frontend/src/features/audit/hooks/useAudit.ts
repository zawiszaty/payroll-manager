import { useQuery } from '@tanstack/react-query'
import { auditApi } from '@/api/audit'
import type { AuditListParams, TimelineParams } from '../types'

const AUDIT_QUERY_KEY = 'audit'

export function useAuditLogs(params?: AuditListParams) {
  return useQuery({
    queryKey: [AUDIT_QUERY_KEY, params],
    queryFn: () => auditApi.list(params),
  })
}

export function useAuditLog(id: string) {
  return useQuery({
    queryKey: [AUDIT_QUERY_KEY, id],
    queryFn: () => auditApi.getById(id),
    enabled: !!id,
  })
}

export function useAuditByEntity(entityType: string, entityId: string) {
  return useQuery({
    queryKey: [AUDIT_QUERY_KEY, 'entity', entityType, entityId],
    queryFn: () => auditApi.getByEntity(entityType, entityId),
    enabled: !!entityType && !!entityId,
  })
}

export function useAuditByEmployee(employeeId: string) {
  return useQuery({
    queryKey: [AUDIT_QUERY_KEY, 'employee', employeeId],
    queryFn: () => auditApi.getByEmployee(employeeId),
    enabled: !!employeeId,
  })
}

export function useAuditTimeline(params?: TimelineParams) {
  return useQuery({
    queryKey: [AUDIT_QUERY_KEY, 'timeline', params],
    queryFn: () => auditApi.getTimeline(params),
  })
}
