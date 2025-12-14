import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { useReport, useDownloadReport } from '../hooks/useReports'
import { REPORT_TYPE_LABELS, REPORT_STATUS_LABELS, REPORT_FORMAT_LABELS } from '../types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate, formatDateTime } from '@/lib/format'

const statusIcons = {
  pending: Clock,
  processing: RefreshCw,
  completed: CheckCircle,
  failed: AlertCircle,
}

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export function ReportDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: report, isLoading, error, refetch } = useReport(id!)
  const downloadReport = useDownloadReport()

  const handleDownload = async () => {
    if (!report || report.status !== 'completed' || !report.file_path) {
      return
    }

    const extension = report.format || 'pdf'
    const filename = `${report.name}_${formatDate(report.created_at)}.${extension}`
    await downloadReport.mutateAsync({ id: report.id, name: filename })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading report...</div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load report</div>
      </div>
    )
  }

  const StatusIcon = statusIcons[report.status as keyof typeof statusIcons] || Clock

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/reports')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{report.name}</h1>
            <p className="text-gray-500">Report Details</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {report.status === 'completed' && report.file_path && (
            <Button onClick={handleDownload}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Report Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <div className="mt-1 flex items-center gap-2">
                <Badge className={statusColors[report.status]}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {REPORT_STATUS_LABELS[report.status as keyof typeof REPORT_STATUS_LABELS] ||
                    report.status}
                </Badge>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Report Type</label>
              <p className="mt-1">
                {REPORT_TYPE_LABELS[report.report_type as keyof typeof REPORT_TYPE_LABELS] ||
                  report.report_type}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Format</label>
              <p className="mt-1">
                {REPORT_FORMAT_LABELS[report.format as keyof typeof REPORT_FORMAT_LABELS] ||
                  report.format}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Created</label>
              <p className="mt-1">{formatDateTime(report.created_at)}</p>
            </div>

            {report.completed_at && (
              <div>
                <label className="text-sm font-medium text-gray-500">Completed</label>
                <p className="mt-1">{formatDateTime(report.completed_at)}</p>
              </div>
            )}

            {report.error_message && (
              <div>
                <label className="text-sm font-medium text-red-500">Error Message</label>
                <p className="mt-1 text-red-600">{report.error_message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            {report.parameters && Object.keys(report.parameters).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(report.parameters).map(([key, value]) => (
                  <div key={key}>
                    <label className="text-sm font-medium text-gray-500 capitalize">
                      {key.replace(/_/g, ' ')}
                    </label>
                    <p className="mt-1">{value || 'N/A'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No parameters specified</p>
            )}
          </CardContent>
        </Card>
      </div>

      {report.status === 'processing' && (
        <Card>
          <CardContent className="py-6">
            <div className="flex items-center justify-center gap-3 text-blue-600">
              <RefreshCw className="h-5 w-5 animate-spin" />
              <p>Report is being generated. Please check back later or refresh the page.</p>
            </div>
          </CardContent>
        </Card>
      )}

      {report.status === 'pending' && (
        <Card>
          <CardContent className="py-6">
            <div className="flex items-center justify-center gap-3 text-gray-600">
              <Clock className="h-5 w-5" />
              <p>Report is queued for generation.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
