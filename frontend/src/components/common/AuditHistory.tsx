import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import type { AuditLogResponse } from '@/api'

interface AuditHistoryProps {
  auditLogs: AuditLogResponse[]
  isLoading?: boolean
}

const ACTION_COLORS: Record<string, string> = {
  created: 'bg-green-100 text-green-800',
  updated: 'bg-blue-100 text-blue-800',
  deleted: 'bg-red-100 text-red-800',
  status_changed: 'bg-yellow-100 text-yellow-800',
  activated: 'bg-green-100 text-green-800',
  canceled: 'bg-red-100 text-red-800',
  expired: 'bg-gray-100 text-gray-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export function AuditHistory({ auditLogs = [], isLoading }: AuditHistoryProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatFieldName = (field: string): string => {
    return field
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const renderValueChange = (oldValue: unknown, newValue: unknown) => {
    // Handle null/undefined values
    if (oldValue === null || oldValue === undefined) {
      return (
        <span>
          Set to <strong>{String(newValue)}</strong>
        </span>
      )
    }
    if (newValue === null || newValue === undefined) {
      return (
        <span>
          Removed from <strong>{String(oldValue)}</strong>
        </span>
      )
    }

    // Handle objects/arrays
    if (typeof oldValue === 'object' || typeof newValue === 'object') {
      return (
        <span>
          Changed from <strong>{JSON.stringify(oldValue)}</strong> to{' '}
          <strong>{JSON.stringify(newValue)}</strong>
        </span>
      )
    }

    return (
      <span>
        Changed from <strong>{String(oldValue)}</strong> to <strong>{String(newValue)}</strong>
      </span>
    )
  }

  const renderChanges = (
    oldValues: Record<string, unknown> | null,
    newValues: Record<string, unknown> | null
  ) => {
    if (!oldValues && !newValues) {
      return <p className="text-sm text-muted-foreground">No details available</p>
    }

    // For creation, show new values
    if (!oldValues && newValues) {
      return (
        <div className="space-y-1 text-sm">
          {Object.entries(newValues).map(([key, value]) => (
            <div key={key}>
              <span className="font-medium">{formatFieldName(key)}:</span>{' '}
              <span>{String(value)}</span>
            </div>
          ))}
        </div>
      )
    }

    // For updates, show what changed
    if (oldValues && newValues) {
      const changedFields = Object.keys(newValues).filter(
        (key) => JSON.stringify(oldValues[key]) !== JSON.stringify(newValues[key])
      )

      if (changedFields.length === 0) {
        return <p className="text-sm text-muted-foreground">No changes detected</p>
      }

      return (
        <div className="space-y-2 text-sm">
          {changedFields.map((field) => (
            <div key={field}>
              <span className="font-medium">{formatFieldName(field)}:</span>{' '}
              {renderValueChange(oldValues[field], newValues[field])}
            </div>
          ))}
        </div>
      )
    }

    // For deletions
    if (oldValues && !newValues) {
      return (
        <div className="space-y-1 text-sm">
          <p className="font-medium text-red-600">Entity deleted</p>
          {Object.entries(oldValues).map(([key, value]) => (
            <div key={key} className="text-muted-foreground">
              <span className="font-medium">{formatFieldName(key)}:</span> {String(value)}
            </div>
          ))}
        </div>
      )
    }

    return null
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Change History</CardTitle>
          <CardDescription>Loading history...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  // Ensure auditLogs is an array
  const logs = Array.isArray(auditLogs) ? auditLogs : []

  if (logs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Change History</CardTitle>
          <CardDescription>No history available</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No changes have been recorded for this entity yet.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change History</CardTitle>
        <CardDescription>
          Showing {logs.length} event{logs.length !== 1 ? 's' : ''}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {logs.map((entry, index) => {
            const timestamp = entry.occurred_at || entry.created_at
            const actionColor = ACTION_COLORS[entry.action] || 'bg-gray-100 text-gray-800'

            return (
              <div key={entry.id}>
                <div className="space-y-2">
                  {/* Header with action and timestamp */}
                  <div className="flex items-center justify-between">
                    <Badge className={actionColor}>{entry.action.toUpperCase()}</Badge>
                    <span className="text-sm text-muted-foreground">{formatDate(timestamp)}</span>
                  </div>

                  {/* Changed by */}
                  {entry.changed_by && (
                    <p className="text-sm text-muted-foreground">
                      By: <span className="font-medium">{entry.changed_by}</span>
                    </p>
                  )}

                  {/* Changes */}
                  <div className="mt-2 rounded-md bg-muted p-3">
                    {renderChanges(entry.old_values, entry.new_values)}
                  </div>

                  {/* Metadata */}
                  {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                        Additional metadata
                      </summary>
                      <pre className="mt-2 overflow-auto rounded bg-muted p-2 text-xs">
                        {JSON.stringify(entry.metadata, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>

                {/* Separator between entries */}
                {index < logs.length - 1 && <Separator className="mt-4" />}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
