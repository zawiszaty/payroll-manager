import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { compensationApi } from '@/api/compensation'
import apiClient from '@/api/client'
import type {
  CreateRateRequest,
  PaginatedResponse_EmployeeListView_,
  EmployeeListView,
  RateType,
} from '@/lib/api'

const RATE_TYPES = [
  { value: 'base_salary', label: 'Base Salary' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'commission', label: 'Commission' },
  { value: 'piece_rate', label: 'Piece Rate' },
]

const CURRENCIES = ['USD', 'EUR', 'GBP', 'PLN']

export function RateForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [employees, setEmployees] = useState<EmployeeListView[]>([])
  const [formData, setFormData] = useState<CreateRateRequest>({
    employee_id: '',
    rate_type: 'base_salary' as RateType,
    amount: 0,
    currency: 'USD',
    valid_from: '',
    valid_to: undefined,
    description: undefined,
  })

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
      setError('Failed to load employees. Please refresh the page.')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!formData.employee_id) {
      setError('Please select an employee')
      return
    }

    if (!formData.valid_from) {
      setError('Please provide a start date')
      return
    }

    const amount =
      typeof formData.amount === 'string' ? parseFloat(formData.amount) : formData.amount

    if (!amount || amount <= 0) {
      setError('Amount must be greater than 0')
      return
    }

    try {
      setLoading(true)

      const rate = await compensationApi.rates.create({
        ...formData,
        amount,
      })

      navigate(`/compensation/rates/${rate.id}`)
    } catch (err: unknown) {
      console.error('Failed to create rate:', err)
      const errorMessage =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined
      setError(errorMessage || 'Failed to create rate. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const updateFormData = (
    field: keyof CreateRateRequest,
    value: CreateRateRequest[keyof CreateRateRequest]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/compensation')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Rate</h1>
          <p className="text-muted-foreground">Create a new employee compensation rate</p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Rate Information</CardTitle>
            <CardDescription>Fill in the details for the new rate</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="employee_id">
                  Employee <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={formData.employee_id}
                  onValueChange={(value) => updateFormData('employee_id', value)}
                >
                  <SelectTrigger id="employee_id">
                    <SelectValue placeholder="Select employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.id}>
                        {employee.first_name} {employee.last_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="rate_type">
                  Rate Type <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={formData.rate_type}
                  onValueChange={(value) => updateFormData('rate_type', value as RateType)}
                >
                  <SelectTrigger id="rate_type">
                    <SelectValue placeholder="Select rate type" />
                  </SelectTrigger>
                  <SelectContent>
                    {RATE_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount">
                  Amount <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.amount || ''}
                  onChange={(e) => updateFormData('amount', parseFloat(e.target.value) || 0)}
                  placeholder="Enter amount"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="currency">
                  Currency <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={formData.currency}
                  onValueChange={(value) => updateFormData('currency', value)}
                >
                  <SelectTrigger id="currency">
                    <SelectValue placeholder="Select currency" />
                  </SelectTrigger>
                  <SelectContent>
                    {CURRENCIES.map((currency) => (
                      <SelectItem key={currency} value={currency}>
                        {currency}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="valid_from">
                  Valid From <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="valid_from"
                  type="date"
                  value={formData.valid_from}
                  onChange={(e) => updateFormData('valid_from', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="valid_to">Valid To (Optional)</Label>
                <Input
                  id="valid_to"
                  type="date"
                  value={formData.valid_to || ''}
                  onChange={(e) => updateFormData('valid_to', e.target.value || undefined)}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  value={formData.description || ''}
                  onChange={(e) => updateFormData('description', e.target.value || undefined)}
                  placeholder="Enter any additional notes or description"
                  rows={3}
                />
              </div>
            </div>

            <div className="flex gap-4 justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/compensation')}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Rate'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
