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
import { contractsApi } from '@/api/contracts'
import apiClient from '@/api/client'
import type {
  CreateContractRequest,
  PaginatedResponse_EmployeeListView_,
  EmployeeListView,
  ContractType,
} from '@/lib/api'

const CONTRACT_TYPES = [
  { value: 'fixed_monthly', label: 'Fixed Monthly' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'b2b_daily', label: 'B2B Daily' },
  { value: 'b2b_hourly', label: 'B2B Hourly' },
  { value: 'task_based', label: 'Task Based' },
  { value: 'commission_based', label: 'Commission Based' },
]

const CURRENCIES = ['USD', 'EUR', 'GBP', 'PLN']

export function ContractForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [employees, setEmployees] = useState<EmployeeListView[]>([])
  const [formData, setFormData] = useState<CreateContractRequest>({
    employee_id: '',
    contract_type: 'fixed_monthly' as ContractType,
    rate_amount: 0,
    rate_currency: 'USD',
    valid_from: '',
    valid_to: undefined,
    hours_per_week: undefined,
    commission_percentage: undefined,
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

    // Validation
    if (!formData.employee_id) {
      setError('Please select an employee')
      return
    }

    if (!formData.valid_from) {
      setError('Please provide a start date')
      return
    }

    const rateAmount =
      typeof formData.rate_amount === 'string'
        ? parseFloat(formData.rate_amount)
        : formData.rate_amount

    if (!rateAmount || rateAmount <= 0) {
      setError('Rate amount must be greater than 0')
      return
    }

    try {
      setLoading(true)

      // Create the contract
      const contract = await contractsApi.create(formData)

      // Navigate to the contract detail page
      navigate(`/contracts/${contract.id}`)
    } catch (err: unknown) {
      console.error('Failed to create contract:', err)
      const errorMessage =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined
      setError(errorMessage || 'Failed to create contract. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const updateFormData = (
    field: keyof CreateContractRequest,
    value: CreateContractRequest[keyof CreateContractRequest]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/contracts')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Contract</h1>
          <p className="text-muted-foreground">Create a new employee contract</p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Contract Information</CardTitle>
            <CardDescription>Fill in the details for the new contract</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Employee Selection */}
            <div className="space-y-2">
              <Label htmlFor="employee_id">Employee *</Label>
              <Select
                value={formData.employee_id}
                onValueChange={(value) => updateFormData('employee_id', value)}
              >
                <SelectTrigger id="employee_id">
                  <SelectValue placeholder="Select an employee" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((employee) => (
                    <SelectItem key={employee.id} value={employee.id}>
                      {employee.first_name} {employee.last_name} - {employee.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Contract Type */}
            <div className="space-y-2">
              <Label htmlFor="contract_type">Contract Type *</Label>
              <Select
                value={formData.contract_type}
                onValueChange={(value) => updateFormData('contract_type', value)}
              >
                <SelectTrigger id="contract_type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CONTRACT_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Rate Amount and Currency */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="rate_amount">Rate Amount *</Label>
                <Input
                  id="rate_amount"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.rate_amount}
                  onChange={(e) => updateFormData('rate_amount', parseFloat(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rate_currency">Currency *</Label>
                <Select
                  value={formData.rate_currency}
                  onValueChange={(value) => updateFormData('rate_currency', value)}
                >
                  <SelectTrigger id="rate_currency">
                    <SelectValue />
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
            </div>

            {/* Dates */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="valid_from">Valid From *</Label>
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
            </div>

            {/* Optional Fields */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="hours_per_week">Hours Per Week (Optional)</Label>
                <Input
                  id="hours_per_week"
                  type="number"
                  min="0"
                  step="0.5"
                  value={formData.hours_per_week || ''}
                  onChange={(e) =>
                    updateFormData(
                      'hours_per_week',
                      e.target.value ? parseFloat(e.target.value) : undefined
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="commission_percentage">Commission Percentage (Optional)</Label>
                <Input
                  id="commission_percentage"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={formData.commission_percentage || ''}
                  onChange={(e) =>
                    updateFormData(
                      'commission_percentage',
                      e.target.value ? parseFloat(e.target.value) : undefined
                    )
                  }
                />
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => updateFormData('description', e.target.value || undefined)}
                placeholder="Add any additional notes about this contract..."
                rows={4}
              />
            </div>

            {/* Form Actions */}
            <div className="flex gap-4 pt-4">
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Contract'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/contracts')}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
