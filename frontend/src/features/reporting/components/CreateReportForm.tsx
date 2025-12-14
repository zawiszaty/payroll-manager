import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText } from 'lucide-react'
import { useCreateReport } from '../hooks/useReports'
import type { CreateReportRequest, ReportType, ReportFormat } from '../types'
import { REPORT_TYPE_LABELS, REPORT_FORMAT_LABELS } from '../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function CreateReportForm() {
  const navigate = useNavigate()
  const createReport = useCreateReport()

  const [formData, setFormData] = useState<CreateReportRequest>({
    name: '',
    report_type: 'payroll_summary',
    format: 'pdf',
    employee_id: null,
    department: null,
    start_date: null,
    end_date: null,
    additional_filters: null,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const result = await createReport.mutateAsync(formData)
      navigate(`/reports/${result.id}`)
    } catch (error) {
      console.error('Failed to create report:', error)
    }
  }

  const handleChange = (field: keyof CreateReportRequest, value: string | null) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value || null,
    }))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/reports')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Create New Report</h1>
          <p className="text-gray-500">Generate a new system report</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Report Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Report Name *</Label>
                <Input
                  id="name"
                  placeholder="e.g., Monthly Payroll January 2024"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="report_type">Report Type *</Label>
                <Select
                  value={formData.report_type}
                  onValueChange={(value) => handleChange('report_type', value as ReportType)}
                >
                  <SelectTrigger id="report_type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(REPORT_TYPE_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="format">Format *</Label>
                <Select
                  value={formData.format}
                  onValueChange={(value) => handleChange('format', value as ReportFormat)}
                >
                  <SelectTrigger id="format">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(REPORT_FORMAT_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department (Optional)</Label>
                <Input
                  id="department"
                  placeholder="e.g., Engineering"
                  value={formData.department || ''}
                  onChange={(e) => handleChange('department', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date (Optional)</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date || ''}
                  onChange={(e) => handleChange('start_date', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="end_date">End Date (Optional)</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date || ''}
                  onChange={(e) => handleChange('end_date', e.target.value)}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => navigate('/reports')}>
                Cancel
              </Button>
              <Button type="submit" disabled={createReport.isPending}>
                {createReport.isPending ? 'Creating...' : 'Create Report'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
