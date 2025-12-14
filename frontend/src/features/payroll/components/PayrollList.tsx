import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, DollarSign } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { usePayrolls } from '../hooks/usePayroll'
import { PayrollStatus } from '../types'

const statusColors: Record<PayrollStatus, string> = {
  [PayrollStatus.DRAFT]: 'bg-gray-500',
  [PayrollStatus.PENDING_APPROVAL]: 'bg-yellow-500',
  [PayrollStatus.APPROVED]: 'bg-blue-500',
  [PayrollStatus.PROCESSED]: 'bg-purple-500',
  [PayrollStatus.PAID]: 'bg-green-500',
  [PayrollStatus.CANCELLED]: 'bg-red-500',
}

export function PayrollList() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [limit] = useState(10)

  const { data, isLoading, error } = usePayrolls(page, limit)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading payrolls...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg text-red-600">
          Error loading payrolls: {(error as Error).message}
        </div>
      </div>
    )
  }

  const payrolls = data?.items || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / limit)

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payrolls</h1>
          <p className="text-gray-600">Manage payroll calculations and payments</p>
        </div>
        <Button onClick={() => navigate('/payrolls/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Payroll
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              All Payrolls ({total})
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {payrolls.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No payrolls found. Create your first payroll to get started.
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee ID</TableHead>
                    <TableHead>Period</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Gross Pay</TableHead>
                    <TableHead>Net Pay</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payrolls.map((payroll) => (
                    <TableRow key={payroll.id}>
                      <TableCell className="font-mono text-sm">
                        {payroll.employee_id.substring(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {formatDate(payroll.period_start_date)} -{' '}
                          {formatDate(payroll.period_end_date)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{payroll.period_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={statusColors[payroll.status]}>
                          {payroll.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatCurrency(payroll.gross_pay, payroll.currency)}</TableCell>
                      <TableCell className="font-semibold">
                        {formatCurrency(payroll.net_pay, payroll.currency)}
                      </TableCell>
                      <TableCell>{formatDate(payroll.created_at)}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/payrolls/${payroll.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-600">
                    Page {page} of {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
