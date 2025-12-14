import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, Plus, CheckCircle2, XCircle, Ban, Eye } from 'lucide-react'
import {
  useAbsences,
  useApproveAbsence,
  useRejectAbsence,
  useCancelAbsence,
} from '../hooks/useAbsences'
import type { Absence } from '../types'
import {
  ABSENCE_TYPE_LABELS,
  ABSENCE_STATUS_LABELS,
  ABSENCE_STATUS_COLORS,
  AbsenceStatus,
} from '../types'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/format'

export function AbsenceList() {
  const navigate = useNavigate()
  const [page] = useState(1)
  const [limit] = useState(100)

  const { data, isLoading, error } = useAbsences(page, limit)
  const approveAbsence = useApproveAbsence()
  const rejectAbsence = useRejectAbsence()
  const cancelAbsence = useCancelAbsence()

  const handleApprove = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await approveAbsence.mutateAsync(id)
  }

  const handleReject = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await rejectAbsence.mutateAsync(id)
  }

  const handleCancel = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await cancelAbsence.mutateAsync(id)
  }

  const calculateDuration = (startDate: string, endDate: string): number => {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    return diffDays
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading absences...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load absences</div>
      </div>
    )
  }

  const absences = data?.items || []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Absences</h1>
          <p className="text-gray-500">Manage employee time off requests</p>
        </div>
        <Button onClick={() => navigate('/absences/new')}>
          <Plus className="h-4 w-4 mr-2" />
          Request Absence
        </Button>
      </div>

      <div className="rounded-lg border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Start Date</TableHead>
              <TableHead>End Date</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {absences.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-gray-500">
                  <Calendar className="mx-auto h-12 w-12 mb-2 opacity-50" />
                  <p>No absences found</p>
                  <p className="text-sm">Create your first absence request to get started</p>
                </TableCell>
              </TableRow>
            ) : (
              absences.map((absence: Absence) => (
                <TableRow key={absence.id}>
                  <TableCell className="font-mono text-sm">
                    {absence.employee_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell>{ABSENCE_TYPE_LABELS[absence.absence_type]}</TableCell>
                  <TableCell>{formatDate(absence.start_date)}</TableCell>
                  <TableCell>{formatDate(absence.end_date)}</TableCell>
                  <TableCell>
                    {calculateDuration(absence.start_date, absence.end_date)} days
                  </TableCell>
                  <TableCell>
                    <Badge className={ABSENCE_STATUS_COLORS[absence.status]}>
                      {ABSENCE_STATUS_LABELS[absence.status]}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">{absence.reason || '-'}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(`/absences/${absence.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {absence.status === AbsenceStatus.PENDING && (
                        <>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={(e) => handleApprove(absence.id, e)}
                            disabled={approveAbsence.isPending}
                          >
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={(e) => handleReject(absence.id, e)}
                            disabled={rejectAbsence.isPending}
                          >
                            <XCircle className="h-4 w-4 text-red-600" />
                          </Button>
                        </>
                      )}
                      {absence.status === AbsenceStatus.APPROVED && (
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={(e) => handleCancel(absence.id, e)}
                          disabled={cancelAbsence.isPending}
                        >
                          <Ban className="h-4 w-4 text-gray-600" />
                        </Button>
                      )}
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
