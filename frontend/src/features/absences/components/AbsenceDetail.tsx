import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, XCircle, Ban, Calendar, User, Clock } from 'lucide-react'
import {
  useAbsence,
  useApproveAbsence,
  useRejectAbsence,
  useCancelAbsence,
} from '../hooks/useAbsences'
import {
  ABSENCE_TYPE_LABELS,
  ABSENCE_STATUS_LABELS,
  ABSENCE_STATUS_COLORS,
  AbsenceStatus,
} from '../types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { formatDate } from '@/lib/format'

export function AbsenceDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: absence, isLoading, error } = useAbsence(id!)
  const approveAbsence = useApproveAbsence()
  const rejectAbsence = useRejectAbsence()
  const cancelAbsence = useCancelAbsence()

  const handleApprove = async () => {
    if (!id) return
    await approveAbsence.mutateAsync(id)
  }

  const handleReject = async () => {
    if (!id) return
    await rejectAbsence.mutateAsync(id)
  }

  const handleCancel = async () => {
    if (!id) return
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
        <div className="text-gray-500">Loading absence...</div>
      </div>
    )
  }

  if (error || !absence) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load absence</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/absences')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">Absence Details</h1>
          <p className="text-gray-500">View and manage absence request</p>
        </div>
        <Badge className={ABSENCE_STATUS_COLORS[absence.status]}>
          {ABSENCE_STATUS_LABELS[absence.status]}
        </Badge>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Request Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <User className="h-4 w-4" />
                  <span>Employee ID</span>
                </div>
                <p className="font-mono text-sm">{absence.employee_id}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  <span>Absence Type</span>
                </div>
                <p className="font-medium">{ABSENCE_TYPE_LABELS[absence.absence_type]}</p>
              </div>
            </div>

            <Separator />

            <div className="grid grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  <span>Start Date</span>
                </div>
                <p className="font-medium">{formatDate(absence.start_date)}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  <span>End Date</span>
                </div>
                <p className="font-medium">{formatDate(absence.end_date)}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>Duration</span>
                </div>
                <p className="font-medium">
                  {calculateDuration(absence.start_date, absence.end_date)} days
                </p>
              </div>
            </div>

            {absence.reason && (
              <>
                <Separator />
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">Reason</p>
                  <p>{absence.reason}</p>
                </div>
              </>
            )}

            {absence.notes && (
              <>
                <Separator />
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">Additional Notes</p>
                  <p className="text-sm">{absence.notes}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {absence.status === AbsenceStatus.PENDING && (
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <Button
                  onClick={handleApprove}
                  disabled={approveAbsence.isPending}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Approve
                </Button>
                <Button
                  onClick={handleReject}
                  disabled={rejectAbsence.isPending}
                  variant="destructive"
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {absence.status === AbsenceStatus.APPROVED && (
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <Button onClick={handleCancel} disabled={cancelAbsence.isPending} variant="outline">
                <Ban className="mr-2 h-4 w-4" />
                Cancel Absence
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
