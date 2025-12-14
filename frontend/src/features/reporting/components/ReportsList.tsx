import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Download, RefreshCw, FileText } from 'lucide-react'
import { useReports, useDownloadReport } from '../hooks/useReports'
import type { ReportResponse } from '../types'
import { REPORT_TYPE_LABELS, REPORT_STATUS_LABELS, REPORT_FORMAT_LABELS } from '../types'
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
import { formatDate, formatDateTime } from '@/lib/format'

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export function ReportsList() {
  const navigate = useNavigate()
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')

  const { data, isLoading, error, refetch } = useReports()
  const downloadReport = useDownloadReport()

  const handleDownload = async (report: ReportResponse) => {
    if (report.status !== 'completed' || !report.file_path) {
      return
    }

    const extension = report.format || 'pdf'
    const filename = `${report.name}_${formatDate(report.created_at)}.${extension}`
    await downloadReport.mutateAsync({ id: report.id, name: filename })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading reports...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load reports</div>
      </div>
    )
  }

  let reports = data?.reports || []

  if (statusFilter !== 'all') {
    reports = reports.filter((r: ReportResponse) => r.status === statusFilter)
  }

  if (typeFilter !== 'all') {
    reports = reports.filter((r: ReportResponse) => r.report_type === typeFilter)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-gray-500">Generate and download system reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => navigate('/reports/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Create Report
          </Button>
        </div>
      </div>

      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>

        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="payroll_summary">Payroll Summary</SelectItem>
            <SelectItem value="employee_compensation">Employee Compensation</SelectItem>
            <SelectItem value="absence_summary">Absence Summary</SelectItem>
            <SelectItem value="timesheet_summary">Timesheet Summary</SelectItem>
            <SelectItem value="tax_report">Tax Report</SelectItem>
            <SelectItem value="custom">Custom</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-lg border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Format</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Completed</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500">
                  No reports found
                </TableCell>
              </TableRow>
            ) : (
              reports.map((report: ReportResponse) => (
                <TableRow key={report.id}>
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-400" />
                      {report.name}
                    </div>
                  </TableCell>
                  <TableCell>
                    {REPORT_TYPE_LABELS[report.report_type as keyof typeof REPORT_TYPE_LABELS] ||
                      report.report_type}
                  </TableCell>
                  <TableCell>
                    {REPORT_FORMAT_LABELS[report.format as keyof typeof REPORT_FORMAT_LABELS] ||
                      report.format}
                  </TableCell>
                  <TableCell>
                    <Badge className={statusColors[report.status]}>
                      {REPORT_STATUS_LABELS[report.status as keyof typeof REPORT_STATUS_LABELS] ||
                        report.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDateTime(report.created_at)}</TableCell>
                  <TableCell>
                    {report.completed_at ? formatDateTime(report.completed_at) : '-'}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(`/reports/${report.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={report.status !== 'completed' || !report.file_path}
                        onClick={() => handleDownload(report)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
