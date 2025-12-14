import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle, ArrowLeft, History, TrendingUp } from 'lucide-react'
import { compensationApi } from '@/api/compensation'
import { auditApi } from '@/api/audit'
import { AuditHistory } from '@/components/common/AuditHistory'
import apiClient from '@/api/client'
import type { BonusView, EmployeeListView, AuditLogResponse } from '@/lib/api'

export function BonusDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [bonus, setBonus] = useState<BonusView | null>(null)
  const [employeeName, setEmployeeName] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [auditLogs, setAuditLogs] = useState<AuditLogResponse[]>([])
  const [auditLoading, setAuditLoading] = useState(false)

  useEffect(() => {
    const loadBonus = async () => {
      if (!id) return

      try {
        setLoading(true)
        setError(null)

        const bonusData = await compensationApi.bonuses.getById(id)
        setBonus(bonusData)

        const employeeResponse = await apiClient.get<EmployeeListView>(
          `/employees/${bonusData.employee_id}`
        )
        setEmployeeName(`${employeeResponse.data.first_name} ${employeeResponse.data.last_name}`)
      } catch (err) {
        console.error('Failed to load bonus:', err)
        setError('Failed to load bonus details. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    loadBonus()
  }, [id])

  useEffect(() => {
    const loadAuditHistory = async () => {
      if (!id || !showHistory) return

      try {
        setAuditLoading(true)
        const logs = await auditApi.getByEntity('bonus', id)
        setAuditLogs(logs)
      } catch (err) {
        console.error('Failed to load audit history:', err)
      } finally {
        setAuditLoading(false)
      }
    }

    loadAuditHistory()
  }, [id, showHistory])

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatCurrency = (amount: string | number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(Number(amount))
  }

  const formatBonusType = (type: string) => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading bonus details...</div>
      </div>
    )
  }

  if (error || !bonus) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => navigate('/compensation')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Compensation
        </Button>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error || 'Bonus not found'}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/compensation')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Compensation
        </Button>
        <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
          <History className="mr-2 h-4 w-4" />
          {showHistory ? 'Hide History' : 'Show History'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle>Bonus Details</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">{employeeName}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Bonus Type</p>
              <Badge variant="secondary" className="text-base">
                {formatBonusType(bonus.bonus_type)}
              </Badge>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Amount</p>
              <p className="text-2xl font-bold">{formatCurrency(bonus.amount, bonus.currency)}</p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Payment Date</p>
              <p className="text-base">{formatDate(bonus.payment_date)}</p>
            </div>

            {bonus.description && (
              <div className="space-y-2 col-span-2">
                <p className="text-sm font-medium text-muted-foreground">Description</p>
                <p className="text-base">{bonus.description}</p>
              </div>
            )}

            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <p className="text-base">{formatDate(bonus.created_at)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {showHistory && <AuditHistory auditLogs={auditLogs} isLoading={auditLoading} />}
    </div>
  )
}
