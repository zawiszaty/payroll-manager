import { useParams, useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { ArrowLeft, Edit, Trash2, History } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
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
import { useEmployee, useDeleteEmployee, useEmployeeHistory } from '../hooks/useEmployees'
import { EmploymentStatus } from '../types'
import { useState } from 'react'

export function EmployeeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const { data: employee, isLoading, error } = useEmployee(id!)
  const { data: history, isLoading: isLoadingHistory } = useEmployeeHistory(id!, showHistory)
  const deleteEmployee = useDeleteEmployee()

  const handleDelete = () => {
    if (id) {
      deleteEmployee.mutate(id, {
        onSuccess: () => {
          navigate('/employees')
        },
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (error || !employee) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600">Error</h2>
          <p className="mt-2 text-gray-600">Failed to load employee details</p>
          <Button onClick={() => navigate('/employees')} className="mt-4">
            Back to Employees
          </Button>
        </div>
      </div>
    )
  }

  const getStatusBadge = (status: EmploymentStatus) => {
    const variants = {
      [EmploymentStatus.ACTIVE]: 'bg-green-100 text-green-800',
      [EmploymentStatus.ON_LEAVE]: 'bg-yellow-100 text-yellow-800',
      [EmploymentStatus.TERMINATED]: 'bg-red-100 text-red-800',
      [EmploymentStatus.SUSPENDED]: 'bg-orange-100 text-orange-800',
    }
    return <Badge className={variants[status]}>{status}</Badge>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/employees')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              {employee.first_name} {employee.last_name}
            </h1>
            <p className="text-gray-600">{employee.email}</p>
          </div>
          {getStatusBadge(employee.status)}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
            <History className="h-4 w-4 mr-2" />
            History
          </Button>
          <Button variant="outline" onClick={() => navigate(`/employees/${id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600">First Name</p>
            <p className="font-medium">{employee.first_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Last Name</p>
            <p className="font-medium">{employee.last_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Email</p>
            <p className="font-medium">{employee.email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Phone</p>
            <p className="font-medium">{employee.phone || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Date of Birth</p>
            <p className="font-medium">
              {employee.date_of_birth ? format(new Date(employee.date_of_birth), 'PPP') : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Personal ID</p>
            <p className="font-medium">{employee.personal_id || 'N/A'}</p>
          </div>
          <div className="col-span-2">
            <p className="text-sm text-gray-600">Address</p>
            <p className="font-medium">
              {employee.address
                ? `${employee.address.street}, ${employee.address.city}, ${employee.address.state} ${employee.address.postal_code}, ${employee.address.country}`
                : 'N/A'}
            </p>
          </div>
          {employee.emergency_contact && (
            <div className="col-span-2">
              <p className="text-sm text-gray-600">Emergency Contact</p>
              <p className="font-medium">
                {employee.emergency_contact.name} ({employee.emergency_contact.relationship}) -{' '}
                {employee.emergency_contact.phone}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Employment Information */}
      <Card>
        <CardHeader>
          <CardTitle>Employment Information</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600">Employee ID</p>
            <p className="font-mono text-sm">{employee.id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Employee Number</p>
            <p className="font-medium">{employee.employee_number}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Employment Type</p>
            <p className="font-medium">{employee.employment_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Position</p>
            <p className="font-medium">{employee.position || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Department</p>
            <p className="font-medium">{employee.department || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Hire Date</p>
            <p className="font-medium">
              {employee.hire_date ? format(new Date(employee.hire_date), 'PPP') : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            {getStatusBadge(employee.status)}
          </div>
          {employee.termination_date && (
            <div>
              <p className="text-sm text-gray-600">Termination Date</p>
              <p className="font-medium">{format(new Date(employee.termination_date), 'PPP')}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* History */}
      {showHistory && (
        <Card>
          <CardHeader>
            <CardTitle>Change History</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingHistory ? (
              <p className="text-gray-600">Loading history...</p>
            ) : history && history.items && history.items.length > 0 ? (
              <div className="space-y-4">
                {history.items.map((entry, index) => {
                  // Use occurred_at or created_at from the audit log
                  const timestamp = entry.occurred_at || entry.created_at
                  const dateObj = new Date(timestamp)
                  const isValidDate = !isNaN(dateObj.getTime())

                  return (
                    <div key={entry.id || index} className="border-l-2 border-gray-300 pl-4">
                      <div className="flex items-center justify-between">
                        <p className="font-medium">{entry.action.toUpperCase()}</p>
                        <p className="text-sm text-gray-600">
                          {isValidDate ? format(dateObj, 'PPp') : 'N/A'}
                        </p>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">Entity: {entry.entity_type}</p>
                      {entry.old_values && (
                        <div className="mt-2 text-sm">
                          <p className="font-medium">Previous Values:</p>
                          <pre className="mt-1 p-2 bg-gray-50 rounded text-xs">
                            {JSON.stringify(entry.old_values, null, 2)}
                          </pre>
                        </div>
                      )}
                      {entry.new_values && (
                        <div className="mt-2 text-sm">
                          <p className="font-medium">New Values:</p>
                          <pre className="mt-1 p-2 bg-gray-50 rounded text-xs">
                            {JSON.stringify(entry.new_values, null, 2)}
                          </pre>
                        </div>
                      )}
                      {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                        <div className="mt-2 text-sm text-gray-600">
                          <p className="text-xs">
                            Source:{' '}
                            {(entry.metadata as { source_event?: string }).source_event ||
                              'Unknown'}
                          </p>
                        </div>
                      )}
                      {index < history.items.length - 1 && <Separator className="mt-4" />}
                    </div>
                  )
                })}
                <div className="mt-4 text-sm text-gray-600">
                  Showing {history.items.length} of {history.total} events
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No history available</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the employee record for {employee.first_name}{' '}
              {employee.last_name}. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={deleteEmployee.isPending}
            >
              {deleteEmployee.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
