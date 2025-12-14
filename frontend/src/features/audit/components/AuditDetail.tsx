import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText } from 'lucide-react'
import { useAuditLog } from '../hooks/useAudit'
import { ACTION_LABELS, ENTITY_TYPE_LABELS } from '../types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDateTime } from '@/lib/format'

const actionColors: Record<string, string> = {
  created: 'bg-green-100 text-green-800',
  updated: 'bg-blue-100 text-blue-800',
  deleted: 'bg-red-100 text-red-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-orange-100 text-orange-800',
  cancelled: 'bg-gray-100 text-gray-800',
  activated: 'bg-teal-100 text-teal-800',
  deactivated: 'bg-slate-100 text-slate-800',
  status_changed: 'bg-purple-100 text-purple-800',
}

export function AuditDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: auditLog, isLoading, error } = useAuditLog(id!)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading audit log...</div>
      </div>
    )
  }

  if (error || !auditLog) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load audit log</div>
      </div>
    )
  }

  const renderValue = (value: unknown): string => {
    if (value === null || value === undefined) return 'null'
    if (typeof value === 'object') return JSON.stringify(value, null, 2)
    return String(value)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/audit')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Audit Log Details</h1>
          <p className="text-gray-500">
            {ENTITY_TYPE_LABELS[auditLog.entity_type] || auditLog.entity_type} -{' '}
            {ACTION_LABELS[auditLog.action] || auditLog.action}
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Event Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Action</label>
              <div className="mt-1">
                <Badge className={actionColors[auditLog.action] || 'bg-gray-100 text-gray-800'}>
                  {ACTION_LABELS[auditLog.action] || auditLog.action}
                </Badge>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Entity Type</label>
              <div className="mt-1 flex items-center gap-2">
                <FileText className="h-4 w-4 text-gray-400" />
                {ENTITY_TYPE_LABELS[auditLog.entity_type] || auditLog.entity_type}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Entity ID</label>
              <p className="mt-1 font-mono text-sm">{auditLog.entity_id}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Occurred At</label>
              <p className="mt-1">{formatDateTime(auditLog.occurred_at)}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Changed By</label>
              <p className="mt-1 font-mono text-sm">{auditLog.changed_by || 'System'}</p>
            </div>

            {auditLog.employee_id && (
              <div>
                <label className="text-sm font-medium text-gray-500">Employee ID</label>
                <p className="mt-1 font-mono text-sm">{auditLog.employee_id}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Metadata</CardTitle>
          </CardHeader>
          <CardContent>
            {auditLog.metadata && Object.keys(auditLog.metadata).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(auditLog.metadata).map(([key, value]) => (
                  <div key={key}>
                    <label className="text-sm font-medium text-gray-500 capitalize">
                      {key.replace(/_/g, ' ')}
                    </label>
                    <p className="mt-1">{renderValue(value)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No metadata available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {auditLog.old_values && Object.keys(auditLog.old_values).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Old Values</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(auditLog.old_values).map(([key, value]) => (
                <div key={key}>
                  <label className="text-sm font-medium text-gray-500 capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <pre className="mt-1 text-sm bg-gray-50 p-2 rounded overflow-auto">
                    {renderValue(value)}
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {auditLog.new_values && Object.keys(auditLog.new_values).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>New Values</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(auditLog.new_values).map(([key, value]) => (
                <div key={key}>
                  <label className="text-sm font-medium text-gray-500 capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <pre className="mt-1 text-sm bg-gray-50 p-2 rounded overflow-auto">
                    {renderValue(value)}
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
