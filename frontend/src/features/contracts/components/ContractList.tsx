import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Plus, AlertCircle, FileText, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { contractsApi } from '@/api/contracts'
import apiClient from '@/api/client'
import type { ContractListView, EmployeeListView } from '@/api'

const CONTRACT_TYPE_LABELS: Record<string, string> = {
  fixed_monthly: 'Fixed Monthly',
  hourly: 'Hourly',
  b2b_daily: 'B2B Daily',
  b2b_hourly: 'B2B Hourly',
  task_based: 'Task Based',
  commission_based: 'Commission Based',
}

const CONTRACT_STATUS_COLORS: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> =
  {
    pending: 'secondary',
    active: 'default',
    expired: 'outline',
    canceled: 'destructive',
  }

interface ContractWithEmployee extends ContractListView {
  employee_name?: string
}

export function ContractList() {
  const navigate = useNavigate()
  const [contracts, setContracts] = useState<ContractWithEmployee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page] = useState(1)

  const loadContracts = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch contracts
      const response = await contractsApi.list(page, 100)
      const contractsList = response.items || []

      // Fetch employees to get names
      const employeesResponse = await apiClient.get('/employees/', {
        params: { page: 1, limit: 100 },
      })
      const employees = employeesResponse.data.items || []

      // Create employee map for quick lookup
      const employeeMap = new Map(
        employees.map((emp: EmployeeListView) => [emp.id, `${emp.first_name} ${emp.last_name}`])
      )

      // Add employee names to contracts
      const contractsWithNames = contractsList.map((contract) => ({
        ...contract,
        employee_name: employeeMap.get(contract.employee_id) || 'Unknown Employee',
      })) as ContractWithEmployee[]

      setContracts(contractsWithNames)
    } catch (err) {
      console.error('Failed to load contracts:', err)
      setError('Failed to load contracts. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    loadContracts()
  }, [loadContracts])

  const filteredContracts = contracts.filter((contract) => {
    const search = searchTerm.toLowerCase()
    return (
      contract.employee_name?.toLowerCase().includes(search) ||
      contract.contract_type?.toLowerCase().includes(search) ||
      contract.status?.toLowerCase().includes(search)
    )
  })

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatAmount = (amount?: string, currency?: string) => {
    if (!amount) return 'N/A'
    const numAmount = parseFloat(amount)
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(numAmount)
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading contracts...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contracts</h1>
          <p className="text-muted-foreground">Manage employee contracts</p>
        </div>
        <Button onClick={() => navigate('/contracts/new')}>
          <Plus className="mr-2 h-4 w-4" />
          New Contract
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search Contracts</CardTitle>
          <CardDescription>Filter contracts by employee, type, or status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by employee, type, or status..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contracts Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Contracts ({filteredContracts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredContracts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="text-lg font-medium">No contracts found</p>
              <p className="text-sm text-muted-foreground">
                {searchTerm
                  ? 'Try adjusting your search'
                  : 'Get started by creating a new contract'}
              </p>
              {!searchTerm && (
                <Button className="mt-4" onClick={() => navigate('/contracts/new')}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Contract
                </Button>
              )}
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead>End Date</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredContracts.map((contract) => (
                    <TableRow
                      key={contract.id}
                      className="cursor-pointer"
                      onClick={() => navigate(`/contracts/${contract.id}`)}
                    >
                      <TableCell className="font-medium">
                        {contract.employee_name || 'Unknown'}
                      </TableCell>
                      <TableCell>
                        {CONTRACT_TYPE_LABELS[contract.contract_type || ''] ||
                          contract.contract_type}
                      </TableCell>
                      <TableCell>
                        <Badge variant={CONTRACT_STATUS_COLORS[contract.status || 'default']}>
                          {contract.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(contract.valid_from)}</TableCell>
                      <TableCell>{formatDate(contract.valid_to)}</TableCell>
                      <TableCell>
                        {formatAmount(contract.rate_amount, contract.rate_currency)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/contracts/${contract.id}`)
                          }}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
