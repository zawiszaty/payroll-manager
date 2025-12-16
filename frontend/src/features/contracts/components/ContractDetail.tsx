import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
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
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertCircle, History } from 'lucide-react'
import { contractsApi } from '@/api/contracts'
import { auditApi } from '@/api/audit'
import apiClient from '@/api/client'
import { AuditHistory } from '@/components/common/AuditHistory'
import type { ContractDetailView, EmployeeDetailView, AuditLogResponse } from '@/api'

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

interface ContractWithEmployee extends ContractDetailView {
  employee_name?: string
}

export function ContractDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [contract, setContract] = useState<ContractWithEmployee | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [showCancelDialog, setShowCancelDialog] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [auditLogs, setAuditLogs] = useState<AuditLogResponse[]>([])
  const [auditLoading, setAuditLoading] = useState(false)

  const loadContract = useCallback(async () => {
    if (!id) return

    try {
      setLoading(true)
      setError(null)

      // Fetch contract
      const contractData = await contractsApi.getById(id)

      // Fetch employee name
      try {
        const employeeResponse = await apiClient.get<EmployeeDetailView>(
          `/employees/${contractData.employee_id}`
        )
        const employeeData = employeeResponse.data
        setContract({
          ...contractData,
          employee_name: `${employeeData.first_name} ${employeeData.last_name}`,
        })
      } catch (empErr) {
        console.warn('Failed to load employee details:', empErr)
        setContract({
          ...contractData,
          employee_name: 'Unknown Employee',
        })
      }
    } catch (err) {
      console.error('Failed to load contract:', err)
      setError('Failed to load contract. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [id])

  const loadAuditHistory = useCallback(async () => {
    if (!id) return

    try {
      setAuditLoading(true)
      const logs = await auditApi.getByEntity('contract', id)
      setAuditLogs(logs)
    } catch (err) {
      console.error('Failed to load audit history:', err)
    } finally {
      setAuditLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (id) {
      loadContract()
    }
  }, [id, loadContract])

  useEffect(() => {
    if (id && showHistory) {
      loadAuditHistory()
    }
  }, [id, showHistory, loadAuditHistory])

  const handleActivate = async () => {
    if (!id) return

    try {
      setActionLoading(true)
      await contractsApi.activate(id)
      await loadContract()
    } catch (err) {
      console.error('Failed to activate contract:', err)
      setError('Failed to activate contract. Please try again.')
    } finally {
      setActionLoading(false)
    }
  }

  const handleCancel = async () => {
    if (!id) return

    try {
      setActionLoading(true)
      await contractsApi.cancel(id, {
        reason: 'Cancelled by user',
      })
      await loadContract()
      setShowCancelDialog(false)
    } catch (err) {
      console.error('Failed to cancel contract:', err)
      setError('Failed to cancel contract. Please try again.')
    } finally {
      setActionLoading(false)
    }
  }

  const handleExpire = async () => {
    if (!id) return

    try {
      setActionLoading(true)
      await contractsApi.expire(id)
      await loadContract()
    } catch (err) {
      console.error('Failed to expire contract:', err)
      setError('Failed to expire contract. Please try again.')
    } finally {
      setActionLoading(false)
    }
  }

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
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
          <p className="mt-2 text-sm text-muted-foreground">Loading contract...</p>
        </div>
      </div>
    )
  }

  if (!contract) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-medium">Contract not found</p>
          <Button className="mt-4" onClick={() => navigate('/contracts')}>
            Back to Contracts
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/contracts')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Contract Details</h1>
            <p className="text-muted-foreground">{contract.employee_name || 'Unknown Employee'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
            <History className="mr-2 h-4 w-4" />
            {showHistory ? 'Hide History' : 'Show History'}
          </Button>
          <Badge variant={CONTRACT_STATUS_COLORS[contract.status || 'default']}>
            {contract.status}
          </Badge>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Contract Information */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Core contract details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Contract Type</label>
              <p className="text-lg">
                {CONTRACT_TYPE_LABELS[contract.terms.contract_type || ''] ||
                  contract.terms.contract_type}
              </p>
            </div>
            <Separator />
            <div>
              <label className="text-sm font-medium text-muted-foreground">Employee</label>
              <p className="text-lg">{contract.employee_name || 'Unknown'}</p>
            </div>
            <Separator />
            <div>
              <label className="text-sm font-medium text-muted-foreground">Rate Amount</label>
              <p className="text-lg">
                {formatAmount(contract.terms.rate_amount, contract.terms.rate_currency)}
              </p>
            </div>
            {contract.terms.hours_per_week && (
              <>
                <Separator />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Hours Per Week
                  </label>
                  <p className="text-lg">{contract.terms.hours_per_week}</p>
                </div>
              </>
            )}
            {contract.terms.commission_percentage && (
              <>
                <Separator />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Commission Percentage
                  </label>
                  <p className="text-lg">{contract.terms.commission_percentage}%</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
            <CardDescription>Contract dates and status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Valid From</label>
              <p className="text-lg">{formatDate(contract.terms.valid_from)}</p>
            </div>
            <Separator />
            <div>
              <label className="text-sm font-medium text-muted-foreground">Valid To</label>
              <p className="text-lg">{formatDate(contract.terms.valid_to)}</p>
            </div>
            <Separator />
            <div>
              <label className="text-sm font-medium text-muted-foreground">Created At</label>
              <p className="text-lg">{formatDate(contract.created_at)}</p>
            </div>
            <Separator />
            <div>
              <label className="text-sm font-medium text-muted-foreground">Version</label>
              <p className="text-lg">{contract.version}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Information */}
      {(contract.terms.description || contract.cancellation_reason) && (
        <Card>
          <CardHeader>
            <CardTitle>Additional Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {contract.terms.description && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">Description</label>
                <p className="text-lg">{contract.terms.description}</p>
              </div>
            )}
            {contract.cancellation_reason && (
              <>
                <Separator />
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Cancellation Reason
                  </label>
                  <p className="text-lg">{contract.cancellation_reason}</p>
                  {contract.canceled_at && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      Cancelled on {formatDate(contract.canceled_at)}
                    </p>
                  )}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>Manage contract status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            {contract.status === 'pending' && (
              <Button onClick={handleActivate} disabled={actionLoading} className="gap-2">
                <CheckCircle className="h-4 w-4" />
                Activate Contract
              </Button>
            )}
            {contract.status === 'active' && (
              <>
                <Button
                  variant="outline"
                  onClick={handleExpire}
                  disabled={actionLoading}
                  className="gap-2"
                >
                  <Clock className="h-4 w-4" />
                  Mark as Expired
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => setShowCancelDialog(true)}
                  disabled={actionLoading}
                  className="gap-2"
                >
                  <XCircle className="h-4 w-4" />
                  Cancel Contract
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Audit History */}
      {showHistory && <AuditHistory auditLogs={auditLogs} isLoading={auditLoading} />}

      {/* Cancel Confirmation Dialog */}
      <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will cancel the contract. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>No, keep it</AlertDialogCancel>
            <AlertDialogAction onClick={handleCancel} disabled={actionLoading}>
              Yes, cancel contract
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
