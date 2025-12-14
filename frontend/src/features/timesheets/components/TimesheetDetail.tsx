import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit, Trash2, History, Send, CheckCircle, XCircle } from 'lucide-react'
import {
  useTimesheet,
  useDeleteTimesheet,
  useSubmitTimesheet,
  useApproveTimesheet,
  useRejectTimesheet,
} from '../hooks/useTimesheets'
import { auditApi } from '@/api/audit'
import type { AuditLogResponse } from '@/api/audit'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { AuditHistory } from '@/components/common/AuditHistory'
import { formatDate, snakeToTitle } from '@/lib/format'
import { TimesheetStatus } from '../types'

const statusColors: Record<TimesheetStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export function TimesheetDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [showSubmitDialog, setShowSubmitDialog] = useState(false)
  const [auditLogs, setAuditLogs] = useState<AuditLogResponse[]>([])
  const [auditLoading, setAuditLoading] = useState(false)
  const [approverUserId, setApproverUserId] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')

  const { data: timesheet, isLoading, error } = useTimesheet(id!)
  const deleteTimesheet = useDeleteTimesheet()
  const submitTimesheet = useSubmitTimesheet()
  const approveTimesheet = useApproveTimesheet()
  const rejectTimesheet = useRejectTimesheet()

  const loadAuditHistory = async () => {
    if (!id) return
    try {
      setAuditLoading(true)
      const logs = await auditApi.getByEntity('timesheet', id)
      setAuditLogs(logs)
    } catch (error) {
      console.error('Failed to load audit history:', error)
    } finally {
      setAuditLoading(false)
    }
  }

  const handleShowHistory = () => {
    if (!showHistory) {
      loadAuditHistory()
    }
    setShowHistory(!showHistory)
  }

  const handleDelete = () => {
    if (id) {
      deleteTimesheet.mutate(id, {
        onSuccess: () => {
          navigate('/timesheets')
        },
      })
    }
  }

  const handleSubmit = () => {
    if (id) {
      submitTimesheet.mutate(id, {
        onSuccess: () => {
          setShowSubmitDialog(false)
        },
      })
    }
  }

  const handleApprove = () => {
    if (id && approverUserId) {
      approveTimesheet.mutate(
        { id, data: { approved_by: approverUserId } },
        {
          onSuccess: () => {
            setShowApproveDialog(false)
            setApproverUserId('')
          },
        }
      )
    }
  }

  const handleReject = () => {
    if (id && rejectionReason) {
      rejectTimesheet.mutate(
        { id, data: { reason: rejectionReason } },
        {
          onSuccess: () => {
            setShowRejectDialog(false)
            setRejectionReason('')
          },
        }
      )
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (error || !timesheet) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600">Error</h2>
          <p className="mt-2 text-gray-600">Failed to load timesheet details</p>
          <Button onClick={() => navigate('/timesheets')} className="mt-4">
            Back to Timesheets
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/timesheets')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Timesheet Details</h1>
            <p className="text-gray-600">
              {formatDate(timesheet.start_date)} - {formatDate(timesheet.end_date)}
            </p>
          </div>
          <Badge className={statusColors[timesheet.status]}>{timesheet.status}</Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleShowHistory}>
            <History className="h-4 w-4 mr-2" />
            {showHistory ? 'Hide History' : 'Show History'}
          </Button>
          {timesheet.status === 'draft' && (
            <>
              <Button variant="outline" onClick={() => navigate(`/timesheets/${id}/edit`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button onClick={() => setShowSubmitDialog(true)}>
                <Send className="h-4 w-4 mr-2" />
                Submit
              </Button>
              <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </>
          )}
          {timesheet.status === 'submitted' && (
            <>
              <Button onClick={() => setShowApproveDialog(true)}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
              <Button variant="destructive" onClick={() => setShowRejectDialog(true)}>
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Timesheet Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-500">Employee ID</Label>
              <p className="font-medium">{timesheet.employee_id}</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">Start Date</Label>
              <p className="font-medium">{formatDate(timesheet.start_date)}</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">End Date</Label>
              <p className="font-medium">{formatDate(timesheet.end_date)}</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">Regular Hours</Label>
              <p className="font-medium">{timesheet.hours}h</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">Overtime Hours</Label>
              <p className="font-medium">
                {timesheet.overtime_hours > 0 ? `${timesheet.overtime_hours}h` : 'None'}
              </p>
            </div>
            {timesheet.overtime_type && (
              <>
                <Separator />
                <div>
                  <Label className="text-gray-500">Overtime Type</Label>
                  <p className="font-medium">{snakeToTitle(timesheet.overtime_type)}</p>
                </div>
              </>
            )}
            <Separator />
            <div>
              <Label className="text-gray-500">Total Hours</Label>
              <p className="font-semibold text-lg">{timesheet.total_hours}h</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Project & Task Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-500">Project ID</Label>
              <p className="font-medium">{timesheet.project_id || 'No project assigned'}</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">Task Description</Label>
              <p className="font-medium whitespace-pre-wrap">
                {timesheet.task_description || 'No description provided'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-500">Current Status</Label>
              <p className="font-medium">
                <Badge className={statusColors[timesheet.status]}>{timesheet.status}</Badge>
              </p>
            </div>
            {timesheet.submitted_at && (
              <>
                <Separator />
                <div>
                  <Label className="text-gray-500">Submitted At</Label>
                  <p className="font-medium">{formatDate(timesheet.submitted_at)}</p>
                </div>
              </>
            )}
            {timesheet.approved_at && (
              <>
                <Separator />
                <div>
                  <Label className="text-gray-500">Approved At</Label>
                  <p className="font-medium">{formatDate(timesheet.approved_at)}</p>
                </div>
              </>
            )}
            {timesheet.approved_by && (
              <>
                <Separator />
                <div>
                  <Label className="text-gray-500">Approved By</Label>
                  <p className="font-medium">{timesheet.approved_by}</p>
                </div>
              </>
            )}
            {timesheet.rejection_reason && (
              <>
                <Separator />
                <div>
                  <Label className="text-gray-500">Rejection Reason</Label>
                  <p className="font-medium text-red-600">{timesheet.rejection_reason}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Metadata</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-500">Created At</Label>
              <p className="font-medium">{formatDate(timesheet.created_at)}</p>
            </div>
            <Separator />
            <div>
              <Label className="text-gray-500">Last Updated</Label>
              <p className="font-medium">{formatDate(timesheet.updated_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {showHistory && <AuditHistory auditLogs={auditLogs} isLoading={auditLoading} />}

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Timesheet</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this timesheet? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submit Timesheet</DialogTitle>
            <DialogDescription>
              Are you sure you want to submit this timesheet for approval? You will not be able to
              edit it after submission.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubmitDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Submit</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Timesheet</DialogTitle>
            <DialogDescription>Enter your user ID to approve this timesheet.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="approver-id">Approver User ID</Label>
              <Input
                id="approver-id"
                value={approverUserId}
                onChange={(e) => setApproverUserId(e.target.value)}
                placeholder="Enter your user ID"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApproveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleApprove} disabled={!approverUserId}>
              Approve
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Timesheet</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this timesheet.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="rejection-reason">Rejection Reason</Label>
              <Textarea
                id="rejection-reason"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Enter rejection reason"
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleReject} disabled={!rejectionReason.trim()}>
              Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
