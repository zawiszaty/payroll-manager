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
import { Plus, AlertCircle, DollarSign, TrendingUp, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { compensationApi } from '@/api/compensation'
import apiClient from '@/api/client'
import type { RateView, BonusView, EmployeeListView } from '@/api'

interface RateWithEmployee extends RateView {
  employee_name?: string
}

interface BonusWithEmployee extends BonusView {
  employee_name?: string
}

export function CompensationList() {
  const navigate = useNavigate()
  const [rates, setRates] = useState<RateWithEmployee[]>([])
  const [bonuses, setBonuses] = useState<BonusWithEmployee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page] = useState(1)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [ratesResponse, bonusesResponse, employeesResponse] = await Promise.all([
        compensationApi.rates.list(page, 100),
        compensationApi.bonuses.list(page, 100),
        apiClient.get('/employees/', { params: { page: 1, limit: 100 } }),
      ])

      const ratesList = ratesResponse.items || []
      const bonusesList = bonusesResponse.items || []
      const employees = employeesResponse.data.items || []

      const employeeMap = new Map(
        employees.map((emp: EmployeeListView) => [emp.id, `${emp.first_name} ${emp.last_name}`])
      )

      const ratesWithNames = ratesList.map((rate) => ({
        ...rate,
        employee_name: employeeMap.get(rate.employee_id) || 'Unknown Employee',
      })) as RateWithEmployee[]

      const bonusesWithNames = bonusesList.map((bonus) => ({
        ...bonus,
        employee_name: employeeMap.get(bonus.employee_id) || 'Unknown Employee',
      })) as BonusWithEmployee[]

      setRates(ratesWithNames)
      setBonuses(bonusesWithNames)
    } catch (err) {
      console.error('Failed to load compensation data:', err)
      setError('Failed to load compensation data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    loadData()
  }, [loadData])

  const filteredRates = rates.filter((rate) => {
    const search = searchTerm.toLowerCase()
    return (
      rate.employee_name?.toLowerCase().includes(search) ||
      rate.rate_type?.toLowerCase().includes(search)
    )
  })

  const filteredBonuses = bonuses.filter((bonus) => {
    const search = searchTerm.toLowerCase()
    return (
      bonus.employee_name?.toLowerCase().includes(search) ||
      bonus.bonus_type?.toLowerCase().includes(search)
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

  const formatCurrency = (amount: string | number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(Number(amount))
  }

  const formatRateType = (type: string) => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading compensation data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Compensation</h1>
          <p className="text-muted-foreground">Manage employee rates and bonuses</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by employee or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <Tabs defaultValue="rates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="rates">
            <DollarSign className="mr-2 h-4 w-4" />
            Rates ({filteredRates.length})
          </TabsTrigger>
          <TabsTrigger value="bonuses">
            <TrendingUp className="mr-2 h-4 w-4" />
            Bonuses ({filteredBonuses.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="rates" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
              <div>
                <CardTitle>Employee Rates</CardTitle>
                <CardDescription>View all employee compensation rates</CardDescription>
              </div>
              <Button onClick={() => navigate('/compensation/rates/new')}>
                <Plus className="mr-2 h-4 w-4" />
                New Rate
              </Button>
            </CardHeader>
            <CardContent>
              {filteredRates.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <DollarSign className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No rates found</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Rate Type</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Valid From</TableHead>
                      <TableHead>Valid To</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRates.map((rate) => (
                      <TableRow
                        key={rate.id}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => navigate(`/compensation/rates/${rate.id}`)}
                      >
                        <TableCell className="font-medium">{rate.employee_name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{formatRateType(rate.rate_type)}</Badge>
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(rate.amount, rate.currency)}
                        </TableCell>
                        <TableCell>{formatDate(rate.valid_from)}</TableCell>
                        <TableCell>{formatDate(rate.valid_to)}</TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/compensation/rates/${rate.id}`)
                            }}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bonuses" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
              <div>
                <CardTitle>Employee Bonuses</CardTitle>
                <CardDescription>View all employee bonuses</CardDescription>
              </div>
              <Button onClick={() => navigate('/compensation/bonuses/new')}>
                <Plus className="mr-2 h-4 w-4" />
                New Bonus
              </Button>
            </CardHeader>
            <CardContent>
              {filteredBonuses.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <TrendingUp className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No bonuses found</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Bonus Type</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Payment Date</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBonuses.map((bonus) => (
                      <TableRow
                        key={bonus.id}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => navigate(`/compensation/bonuses/${bonus.id}`)}
                      >
                        <TableCell className="font-medium">{bonus.employee_name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{formatRateType(bonus.bonus_type)}</Badge>
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(bonus.amount, bonus.currency)}
                        </TableCell>
                        <TableCell>{formatDate(bonus.payment_date)}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {bonus.description || '-'}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/compensation/bonuses/${bonus.id}`)
                            }}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
