import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { ArrowLeft } from 'lucide-react'
import { useCreateAbsence } from '../hooks/useAbsences'
import { useEmployees } from '@/features/employees/hooks/useEmployees'
import { AbsenceType, ABSENCE_TYPE_LABELS } from '../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const absenceFormSchema = z
  .object({
    employee_id: z.string().uuid('Please select an employee'),
    absence_type: z.nativeEnum(AbsenceType, {
      required_error: 'Please select an absence type',
    }),
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
    reason: z.string().optional(),
    notes: z.string().optional(),
  })
  .refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
    message: 'End date must be after or equal to start date',
    path: ['end_date'],
  })

type AbsenceFormValues = z.infer<typeof absenceFormSchema>

export function AbsenceForm() {
  const navigate = useNavigate()
  const { data: employeesData } = useEmployees({ limit: 100 })
  const createAbsence = useCreateAbsence()

  const form = useForm<AbsenceFormValues>({
    resolver: zodResolver(absenceFormSchema),
    defaultValues: {
      employee_id: '',
      absence_type: AbsenceType.VACATION,
      start_date: '',
      end_date: '',
      reason: '',
      notes: '',
    },
  })

  const onSubmit = async (data: AbsenceFormValues) => {
    try {
      await createAbsence.mutateAsync({
        employee_id: data.employee_id,
        absence_type: data.absence_type,
        start_date: data.start_date,
        end_date: data.end_date,
        reason: data.reason || undefined,
        notes: data.notes || undefined,
      })
      navigate('/absences')
    } catch (error) {
      console.error('Failed to create absence:', error)
    }
  }

  const employees = employeesData?.items || []

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/absences')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Request Absence</h1>
          <p className="text-gray-500">Submit a new absence request</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Absence Details</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="employee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Employee *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an employee" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {employees.map((employee) => (
                          <SelectItem key={employee.id} value={employee.id}>
                            {employee.first_name} {employee.last_name} ({employee.email})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="absence_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Absence Type *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select absence type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {Object.values(AbsenceType).map((type) => (
                          <SelectItem key={type} value={type}>
                            {ABSENCE_TYPE_LABELS[type]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="start_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Start Date *</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="end_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End Date *</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="reason"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reason</FormLabel>
                    <FormControl>
                      <Input placeholder="Brief reason for absence" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Additional Notes</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Any additional information..."
                        className="min-h-[100px]"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-4">
                <Button type="submit" disabled={createAbsence.isPending}>
                  {createAbsence.isPending ? 'Creating...' : 'Submit Request'}
                </Button>
                <Button type="button" variant="outline" onClick={() => navigate('/absences')}>
                  Cancel
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
