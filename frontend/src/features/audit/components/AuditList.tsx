import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RefreshCw, FileText, Eye } from 'lucide-react'
import { useAuditLogs } from '../hooks/useAudit'
import type { AuditLogResponse } from '../types'
import { ACTION_LABELS, ENTITY_TYPE_LABELS } from '../types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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

export function AuditList() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>('all')
  const [actionFilter, setActionFilter] = useState<string>('all')

  const { data, isLoading, error, refetch } = useAuditLogs({
    page,
    limit: pageSize,
    entity_type: entityTypeFilter === 'all' ? null : entityTypeFilter,
    action: actionFilter === 'all' ? null : actionFilter,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading audit logs...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load audit logs</div>
      </div>
    )
  }

  const auditLogs = data?.items || []
  const total = data?.total || 0

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Audit Logs</h1>
          <p className="text-gray-500">View all system changes and activities</p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="flex gap-4">
        <Select value={entityTypeFilter} onValueChange={setEntityTypeFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by entity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Entities</SelectItem>
            {Object.entries(ENTITY_TYPE_LABELS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={actionFilter} onValueChange={setActionFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by action" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Actions</SelectItem>
            {Object.entries(ACTION_LABELS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-lg border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Entity Type</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Entity ID</TableHead>
              <TableHead>Changed By</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {auditLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-gray-500">
                  No audit logs found
                </TableCell>
              </TableRow>
            ) : (
              auditLogs.map((log: AuditLogResponse) => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">{formatDateTime(log.occurred_at)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-400" />
                      {ENTITY_TYPE_LABELS[log.entity_type] || log.entity_type}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={actionColors[log.action] || 'bg-gray-100 text-gray-800'}>
                      {ACTION_LABELS[log.action] || log.action}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {log.entity_id.substring(0, 8)}...
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {log.changed_by ? log.changed_by.substring(0, 8) + '...' : 'System'}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => navigate(`/audit/${log.id}`)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {total > pageSize && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}{' '}
            audit logs
          </div>
          <div className="flex gap-2">
            <Button variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>
              Previous
            </Button>
            <Button
              variant="outline"
              disabled={page * pageSize >= total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
