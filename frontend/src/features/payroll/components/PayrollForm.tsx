import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useNavigate } from 'react-router-dom'
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
import { useCreatePayroll } from '../hooks/usePayroll'
import { PayrollPeriodType } from '../types'
import apiClient from '@/api/client'
import type { PaginatedResponse_EmployeeListView_, EmployeeListView } from '@/api'

const payrollSchema = z
  .object({
    employee_id: z.string().min(1, 'Employee is required'),
    period_type: z.nativeEnum(PayrollPeriodType, {
      required_error: 'Period type is required',
    }),
    period_start_date: z.string().min(1, 'Start date is required'),
    period_end_date: z.string().min(1, 'End date is required'),
    notes: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.period_end_date < data.period_start_date) {
        return false
      }
      return true
    },
    {
      message: 'End date must be after or equal to start date',
      path: ['period_end_date'],
    }
  )

type PayrollFormValues = z.infer<typeof payrollSchema>

export function PayrollForm() {
  const navigate = useNavigate()
  const [employees, setEmployees] = useState<EmployeeListView[]>([])
  const createPayroll = useCreatePayroll()

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

  const form = useForm<PayrollFormValues>({
    resolver: zodResolver(payrollSchema),
    mode: 'onChange',
    defaultValues: {
      employee_id: '',
      period_type: undefined,
      period_start_date: '',
      period_end_date: '',
      notes: '',
    },
  })

  const onSubmit = (data: PayrollFormValues) => {
    createPayroll.mutate(
      {
        employee_id: data.employee_id,
        period_type: data.period_type,
        period_start_date: data.period_start_date,
        period_end_date: data.period_end_date,
        notes: data.notes || undefined,
      },
      {
        onSuccess: (newPayroll) => {
          navigate(`/payrolls/${newPayroll.id}`)
        },
      }
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/payrolls')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create Payroll</h1>
          <p className="text-gray-600">Add a new payroll entry for an employee</p>
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
                    <Select onValueChange={field.onChange} value={field.value}>
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
                    <FormDescription>Select the employee for this payroll period</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="period_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Period Type</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select period type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={PayrollPeriodType.WEEKLY}>Weekly</SelectItem>
                        <SelectItem value={PayrollPeriodType.BIWEEKLY}>Bi-weekly</SelectItem>
                        <SelectItem value={PayrollPeriodType.MONTHLY}>Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>How frequently is this employee paid?</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="period_start_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Period Start Date</FormLabel>
                    <FormControl>
                      <Input {...field} type="date" />
                    </FormControl>
                    <FormDescription>First day of the payroll period</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="period_end_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Period End Date</FormLabel>
                    <FormControl>
                      <Input {...field} type="date" />
                    </FormControl>
                    <FormDescription>Last day of the payroll period</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes (Optional)</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="Add any notes about this payroll period..."
                        rows={4}
                      />
                    </FormControl>
                    <FormDescription>Any additional information about this payroll</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate('/payrolls')}>
              Cancel
            </Button>
            <Button type="submit" disabled={createPayroll.isPending}>
              <Save className="h-4 w-4 mr-2" />
              Create Payroll
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}
