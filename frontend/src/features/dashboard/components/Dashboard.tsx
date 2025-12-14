import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Users, FileText, Calendar, AlertCircle } from 'lucide-react'
import apiClient from '@/api/client'
import type {
  PaginatedResponse_EmployeeListView_,
  PaginatedResponse_ContractListView_,
  PaginatedResponse_AbsenceResponse_,
  AbsenceResponse,
} from '@/lib/api'

interface DashboardStats {
  totalEmployees: number
  activeEmployees: number
  totalContracts: number
  activeContracts: number
  pendingAbsences: number
  totalAbsences: number
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalEmployees: 0,
    activeEmployees: 0,
    totalContracts: 0,
    activeContracts: 0,
    pendingAbsences: 0,
    totalAbsences: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all data in parallel
      const [employeesRes, contractsRes, absencesRes] = await Promise.all([
        apiClient.get<PaginatedResponse_EmployeeListView_>('/employees/', {
          params: { page: 1, limit: 1 },
        }),
        apiClient.get<PaginatedResponse_ContractListView_>('/contracts/', {
          params: { page: 1, limit: 1 },
        }),
        apiClient.get<PaginatedResponse_AbsenceResponse_>('/absence/absences/', {
          params: { page: 1, limit: 100 },
        }),
      ])

      // Calculate stats
      const totalEmployees = (employeesRes.data.items || []).length
      const totalContracts = (contractsRes.data.items || []).length
      const absences: AbsenceResponse[] = absencesRes.data.items || []

      // Count active employees (you might need to filter based on status)
      const activeEmployees = totalEmployees // Adjust based on actual status filtering

      // Count active contracts (you might need to filter based on status)
      const activeContracts = totalContracts // Adjust based on actual status filtering

      // Count pending absences
      const pendingAbsences = absences.filter((a) => a.status === 'pending').length
      const totalAbsences = absences.length

      setStats({
        totalEmployees,
        activeEmployees,
        totalContracts,
        activeContracts,
        pendingAbsences,
        totalAbsences,
      })
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Failed to load dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your payroll management system</p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Employees Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}</div>
            <p className="text-xs text-muted-foreground">{stats.activeEmployees} active</p>
          </CardContent>
        </Card>

        {/* Contracts Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Contracts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalContracts}</div>
            <p className="text-xs text-muted-foreground">{stats.activeContracts} active</p>
          </CardContent>
        </Card>

        {/* Absences Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Absences</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingAbsences}</div>
            <p className="text-xs text-muted-foreground">{stats.totalAbsences} total this period</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and actions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <a
              href="/employees/new"
              className="block rounded-lg border p-3 transition-colors hover:bg-accent"
            >
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="font-medium">Add New Employee</span>
              </div>
            </a>
            <a
              href="/contracts"
              className="block rounded-lg border p-3 transition-colors hover:bg-accent"
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span className="font-medium">Manage Contracts</span>
              </div>
            </a>
            <a
              href="/absences"
              className="block rounded-lg border p-3 transition-colors hover:bg-accent"
            >
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span className="font-medium">Review Absences</span>
              </div>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Current system information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Last Updated</span>
              <span className="text-sm font-medium">{new Date().toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                Operational
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
