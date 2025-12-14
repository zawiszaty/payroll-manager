import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Calculator, CheckCircle, PlayCircle, DollarSign, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  usePayroll,
  useCalculatePayroll,
  useApprovePayroll,
  useProcessPayroll,
  useMarkPayrollAsPaid,
} from '../hooks/usePayroll'
import { PayrollStatus, PayrollLineType } from '../types'
import { useAppSelector } from '@/store/hooks'

const statusColors: Record<PayrollStatus, string> = {
  [PayrollStatus.DRAFT]: 'bg-gray-500',
  [PayrollStatus.PENDING_APPROVAL]: 'bg-yellow-500',
  [PayrollStatus.APPROVED]: 'bg-blue-500',
  [PayrollStatus.PROCESSED]: 'bg-purple-500',
  [PayrollStatus.PAID]: 'bg-green-500',
  [PayrollStatus.CANCELLED]: 'bg-red-500',
}

const lineTypeColors: Record<PayrollLineType, string> = {
  [PayrollLineType.BASE_SALARY]: 'bg-blue-100 text-blue-800',
  [PayrollLineType.HOURLY_WAGE]: 'bg-blue-100 text-blue-800',
  [PayrollLineType.OVERTIME]: 'bg-green-100 text-green-800',
  [PayrollLineType.BONUS]: 'bg-purple-100 text-purple-800',
  [PayrollLineType.COMMISSION]: 'bg-purple-100 text-purple-800',
  [PayrollLineType.DEDUCTION]: 'bg-red-100 text-red-800',
  [PayrollLineType.TAX]: 'bg-orange-100 text-orange-800',
  [PayrollLineType.ABSENCE_DEDUCTION]: 'bg-red-100 text-red-800',
}

export function PayrollDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)

  const { data: payroll, isLoading } = usePayroll(id!)
  const calculatePayroll = useCalculatePayroll()
  const approvePayroll = useApprovePayroll()
  const processPayroll = useProcessPayroll()
  const markAsPaid = useMarkPayrollAsPaid()

  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showMarkPaidDialog, setShowMarkPaidDialog] = useState(false)
  const [paymentReference, setPaymentReference] = useState('')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg">Loading payroll details...</div>
      </div>
    )
  }

  if (!payroll) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-lg text-red-600">Payroll not found</div>
      </div>
    )
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  const formatCurrency = (amount: number | string, currency: string) => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(numAmount)
  }

  const parseAmount = (amount: number | string): number => {
    return typeof amount === 'string' ? parseFloat(amount) : amount
  }

  const handleCalculate = () => {
    calculatePayroll.mutate({ id: id!, data: {} })
  }

  const handleApprove = () => {
    if (!user?.id) {
      console.error('No user ID available for approval')
      return
    }
    approvePayroll.mutate(
      { id: id!, data: { approved_by: user.id } },
      {
        onSuccess: () => setShowApproveDialog(false),
      }
    )
  }

  const handleProcess = () => {
    processPayroll.mutate(id!)
  }

  const handleMarkPaid = () => {
    markAsPaid.mutate(
      { id: id!, data: { payment_reference: paymentReference } },
      {
        onSuccess: () => {
          setShowMarkPaidDialog(false)
          setPaymentReference('')
        },
      }
    )
  }

  const canCalculate = payroll.status === PayrollStatus.DRAFT
  const canApprove = payroll.status === PayrollStatus.PENDING_APPROVAL
  const canProcess = payroll.status === PayrollStatus.APPROVED
  const canMarkPaid = payroll.status === PayrollStatus.PROCESSED

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/payrolls')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">Payroll Details</h1>
          <p className="text-gray-600">
            {formatDate(payroll.period_start_date)} - {formatDate(payroll.period_end_date)}
          </p>
        </div>
        <Badge className={statusColors[payroll.status]}>{payroll.status.replace('_', ' ')}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Gross Pay</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(payroll.gross_pay, payroll.currency)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Deductions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(
                parseAmount(payroll.total_deductions) + parseAmount(payroll.total_taxes),
                payroll.currency
              )}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Deductions: {formatCurrency(payroll.total_deductions, payroll.currency)}
            </div>
            <div className="text-sm text-gray-600">
              Taxes: {formatCurrency(payroll.total_taxes, payroll.currency)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Net Pay</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(payroll.net_pay, payroll.currency)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">Employee ID</div>
              <div className="font-mono">{payroll.employee_id}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Period Type</div>
              <div>
                <Badge variant="outline">{payroll.period_type}</Badge>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Created</div>
              <div>{formatDate(payroll.created_at)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Last Updated</div>
              <div>{formatDate(payroll.updated_at)}</div>
            </div>
            {payroll.approved_at && (
              <>
                <div>
                  <div className="text-sm text-gray-600">Approved At</div>
                  <div>{formatDateTime(payroll.approved_at)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Approved By</div>
                  <div className="font-mono text-sm">{payroll.approved_by}</div>
                </div>
              </>
            )}
            {payroll.processed_at && (
              <div>
                <div className="text-sm text-gray-600">Processed At</div>
                <div>{formatDateTime(payroll.processed_at)}</div>
              </div>
            )}
            {payroll.paid_at && (
              <>
                <div>
                  <div className="text-sm text-gray-600">Paid At</div>
                  <div>{formatDateTime(payroll.paid_at)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Payment Reference</div>
                  <div className="font-mono text-sm">{payroll.payment_reference}</div>
                </div>
              </>
            )}
          </div>
          {payroll.notes && (
            <div>
              <div className="text-sm text-gray-600">Notes</div>
              <div className="mt-1">{payroll.notes}</div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Payroll Line Items
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {payroll.lines.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No line items. Calculate payroll to generate line items.
            </div>
          ) : (
            <div className="space-y-2">
              {payroll.lines.map((line, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Badge className={lineTypeColors[line.line_type]}>
                        {line.line_type.replace('_', ' ')}
                      </Badge>
                      <span className="font-medium">{line.description}</span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {line.quantity} × {formatCurrency(line.rate, line.currency)}
                    </div>
                  </div>
                  <div className="text-lg font-semibold">
                    {formatCurrency(line.amount, line.currency)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button onClick={handleCalculate} disabled={!canCalculate || calculatePayroll.isPending}>
            <Calculator className="h-4 w-4 mr-2" />
            Calculate Payroll
          </Button>

          <Button
            onClick={() => setShowApproveDialog(true)}
            disabled={!canApprove || approvePayroll.isPending}
            variant="outline"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Approve Payroll
          </Button>

          <Button
            onClick={handleProcess}
            disabled={!canProcess || processPayroll.isPending}
            variant="outline"
          >
            <PlayCircle className="h-4 w-4 mr-2" />
            Process Payroll
          </Button>

          <Button
            onClick={() => setShowMarkPaidDialog(true)}
            disabled={!canMarkPaid || markAsPaid.isPending}
            variant="outline"
          >
            <DollarSign className="h-4 w-4 mr-2" />
            Mark as Paid
          </Button>
        </CardContent>
      </Card>

      {/* Approve Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Payroll</DialogTitle>
            <DialogDescription>
              Are you sure you want to approve this payroll? This action will move it to the
              approved state.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApproveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleApprove} disabled={approvePayroll.isPending}>
              Approve
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Mark Paid Dialog */}
      <Dialog open={showMarkPaidDialog} onOpenChange={setShowMarkPaidDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark as Paid</DialogTitle>
            <DialogDescription>
              Enter the payment reference number to mark this payroll as paid.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="payment-reference">Payment Reference</Label>
            <Input
              id="payment-reference"
              value={paymentReference}
              onChange={(e) => setPaymentReference(e.target.value)}
              placeholder="e.g., TXN-2024-001"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMarkPaidDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleMarkPaid} disabled={markAsPaid.isPending || !paymentReference}>
              Mark as Paid
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
