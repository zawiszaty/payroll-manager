import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useTimesheet, useCreateTimesheet, useUpdateTimesheet } from '../hooks/useTimesheets'
import { OvertimeType } from '../types'
import apiClient from '@/api/client'
import type { PaginatedResponse_EmployeeListView_, EmployeeListView } from '@/lib/api'

const timesheetSchema = z
  .object({
    employee_id: z.string().min(1, 'Employee ID is required'),
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
    hours: z.coerce.number().min(0, 'Hours must be positive').max(24, 'Hours cannot exceed 24'),
    overtime_hours: z.coerce
      .number()
      .min(0, 'Overtime hours must be positive')
      .max(24, 'Overtime hours cannot exceed 24'),
    overtime_type: z.string().optional().nullable(),
    project_id: z.string().optional().nullable(),
    task_description: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.overtime_hours > 0 && !data.overtime_type) {
        return false
      }
      if (data.end_date < data.start_date) {
        return false
      }
      return true
    },
    {
      message:
        'Overtime type is required when overtime hours > 0, and end date must be after start date',
      path: ['overtime_type'],
    }
  )

type TimesheetFormValues = z.infer<typeof timesheetSchema>

export function TimesheetForm() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditMode = Boolean(id)
  const [employees, setEmployees] = useState<EmployeeListView[]>([])

  const { data: timesheet, isLoading } = useTimesheet(isEditMode ? id! : '')
  const createTimesheet = useCreateTimesheet()
  const updateTimesheet = useUpdateTimesheet()

  useEffect(() => {
    loadEmployees()
  }, [])

  const loadEmployees = async () => {
    try {
      const response = await apiClient.get<PaginatedResponse_EmployeeListView_>('/employees/', {
        params: { page: 1, limit: 100 },
      })
      setEmployees(response.data.items || [])
    } catch (err) {
      console.error('Failed to load employees:', err)
    }
  }

  const form = useForm<TimesheetFormValues>({
    resolver: zodResolver(timesheetSchema),
    mode: 'onChange',
    defaultValues: {
      employee_id: '',
      start_date: '',
      end_date: '',
      hours: 0,
      overtime_hours: 0,
      overtime_type: null,
      project_id: null,
      task_description: '',
    },
  })

  const overtimeHours = form.watch('overtime_hours')

  // Reset overtime_type when overtime_hours becomes 0
  useEffect(() => {
    if (overtimeHours === 0 || overtimeHours === null || overtimeHours === undefined) {
      form.setValue('overtime_type', null)
    }
  }, [overtimeHours, form])

  useEffect(() => {
    if (timesheet && isEditMode) {
      form.reset({
        employee_id: timesheet.employee_id,
        start_date: timesheet.start_date,
        end_date: timesheet.end_date,
        hours: timesheet.hours,
        overtime_hours: timesheet.overtime_hours,
        overtime_type: timesheet.overtime_type || null,
        project_id: timesheet.project_id || null,
        task_description: timesheet.task_description || '',
      })
    }
  }, [timesheet, isEditMode, form])

  const onSubmit = (data: TimesheetFormValues) => {
    if (isEditMode && id) {
      const updatePayload = {
        hours: data.hours,
        overtime_hours: data.overtime_hours,
        overtime_type: data.overtime_type || null,
        project_id: data.project_id || null,
        task_description: data.task_description || null,
      }
      updateTimesheet.mutate(
        { id, data: updatePayload },
        {
          onSuccess: () => {
            navigate(`/timesheets/${id}`)
          },
        }
      )
    } else {
      const createPayload = {
        employee_id: data.employee_id,
        start_date: data.start_date,
        end_date: data.end_date,
        hours: data.hours,
        overtime_hours: data.overtime_hours,
        overtime_type:
          data.overtime_hours > 0 && data.overtime_type
            ? (data.overtime_type as OvertimeType)
            : null,
        project_id: data.project_id || null,
        task_description: data.task_description || null,
      }
      createTimesheet.mutate(createPayload, {
        onSuccess: (newTimesheet) => {
          navigate(`/timesheets/${newTimesheet.id}`)
        },
      })
    }
  }

  if (isLoading && isEditMode) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/timesheets')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {isEditMode ? 'Edit Timesheet' : 'Create Timesheet'}
          </h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update timesheet information' : 'Add a new timesheet entry'}
          </p>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="employee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Employee</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={isEditMode}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an employee" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {employees.map((employee) => (
                          <SelectItem key={employee.id} value={employee.id}>
                            {employee.first_name} {employee.last_name} - {employee.email}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      {isEditMode
                        ? 'Employee cannot be changed'
                        : 'Select the employee for this timesheet'}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="start_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start Date</FormLabel>
                    <FormControl>
                      <Input {...field} type="date" disabled={isEditMode} />
                    </FormControl>
                    <FormDescription>
                      {isEditMode ? 'Start date cannot be changed' : 'First day of period'}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="end_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>End Date</FormLabel>
                    <FormControl>
                      <Input {...field} type="date" disabled={isEditMode} />
                    </FormControl>
                    <FormDescription>
                      {isEditMode ? 'End date cannot be changed' : 'Last day of period'}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="hours"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Regular Hours</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" step="0.5" min="0" max="24" placeholder="8" />
                    </FormControl>
                    <FormDescription>Number of regular working hours (0-24)</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="overtime_hours"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Overtime Hours</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" step="0.5" min="0" max="24" placeholder="0" />
                    </FormControl>
                    <FormDescription>Number of overtime hours (0-24)</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {overtimeHours > 0 && (
                <FormField
                  control={form.control}
                  name="overtime_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Overtime Type</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value || undefined}
                        value={field.value || undefined}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select overtime type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value={OvertimeType.REGULAR}>Regular</SelectItem>
                          <SelectItem value={OvertimeType.WEEKEND}>Weekend</SelectItem>
                          <SelectItem value={OvertimeType.HOLIDAY}>Holiday</SelectItem>
                          <SelectItem value={OvertimeType.NIGHT_SHIFT}>Night Shift</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>Required when overtime hours &gt; 0</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Project & Task Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="project_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Project ID (Optional)</FormLabel>
                    <FormControl>
                      <Input {...field} value={field.value || ''} placeholder="Enter project ID" />
                    </FormControl>
                    <FormDescription>
                      UUID of the project this work is associated with
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="task_description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Task Description (Optional)</FormLabel>
                    <FormControl>
                      <Textarea {...field} placeholder="Describe the work performed..." rows={4} />
                    </FormControl>
                    <FormDescription>Brief description of the work performed</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate('/timesheets')}>
              Cancel
            </Button>
            <Button type="submit" disabled={createTimesheet.isPending || updateTimesheet.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {isEditMode ? 'Update' : 'Create'} Timesheet
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}
