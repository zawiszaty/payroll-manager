import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Edit, Trash2, Send } from 'lucide-react'
import { useTimesheets, useDeleteTimesheet, useSubmitTimesheet } from '../hooks/useTimesheets'
import type { Timesheet, TimesheetStatus } from '../types'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { formatDate } from '@/lib/format'

const statusColors: Record<TimesheetStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export function TimesheetList() {
  const navigate = useNavigate()
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; timesheet?: Timesheet }>({
    open: false,
  })
  const [submitDialog, setSubmitDialog] = useState<{ open: boolean; timesheet?: Timesheet }>({
    open: false,
  })

  const { data: timesheets, isLoading, error } = useTimesheets()
  const deleteTimesheet = useDeleteTimesheet()
  const submitTimesheet = useSubmitTimesheet()

  const handleDelete = async () => {
    if (deleteDialog.timesheet) {
      await deleteTimesheet.mutateAsync(deleteDialog.timesheet.id)
      setDeleteDialog({ open: false })
    }
  }

  const handleSubmit = async () => {
    if (submitDialog.timesheet) {
      await submitTimesheet.mutateAsync(submitDialog.timesheet.id)
      setSubmitDialog({ open: false })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-gray-500">Loading timesheets...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-red-500">Failed to load timesheets</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Timesheets</h1>
          <p className="text-gray-500">Manage timesheet entries and approvals</p>
        </div>
        <Button onClick={() => navigate('/timesheets/new')}>
          <Plus className="h-4 w-4 mr-2" />
          Create Timesheet
        </Button>
      </div>

      <div className="rounded-lg border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee ID</TableHead>
              <TableHead>Work Date</TableHead>
              <TableHead>Regular Hours</TableHead>
              <TableHead>Overtime Hours</TableHead>
              <TableHead>Total Hours</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {!timesheets || timesheets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500">
                  No timesheets found
                </TableCell>
              </TableRow>
            ) : (
              timesheets.map((timesheet) => (
                <TableRow key={timesheet.id}>
                  <TableCell className="font-medium">
                    {timesheet.employee_id.substring(0, 8)}...
                  </TableCell>
                  <TableCell>{formatDate(timesheet.work_date)}</TableCell>
                  <TableCell>{timesheet.hours}h</TableCell>
                  <TableCell>
                    {timesheet.overtime_hours > 0 ? (
                      <>
                        {timesheet.overtime_hours}h
                        {timesheet.overtime_type && (
                          <span className="text-xs text-gray-500 ml-1">
                            ({timesheet.overtime_type})
                          </span>
                        )}
                      </>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell className="font-semibold">{timesheet.total_hours}h</TableCell>
                  <TableCell>
                    <Badge className={statusColors[timesheet.status]}>{timesheet.status}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(`/timesheets/${timesheet.id}`)}
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {timesheet.status === 'draft' && (
                        <>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => navigate(`/timesheets/${timesheet.id}/edit`)}
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setSubmitDialog({ open: true, timesheet })}
                            title="Submit for approval"
                          >
                            <Send className="h-4 w-4 text-blue-500" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setDeleteDialog({ open: true, timesheet })}
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Timesheet</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this timesheet entry for{' '}
              {deleteDialog.timesheet?.work_date}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog({ open: false })}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={submitDialog.open} onOpenChange={(open) => setSubmitDialog({ open })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submit Timesheet</DialogTitle>
            <DialogDescription>
              Are you sure you want to submit this timesheet for approval? You will not be able to
              edit it after submission.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSubmitDialog({ open: false })}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Submit</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
