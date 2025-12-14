import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginForm } from '@/features/auth/components/LoginForm'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import { AppLayout } from '@/components/layout/AppLayout'
import { EmployeeList } from '@/features/employees/components/EmployeeList'
import { EmployeeDetail } from '@/features/employees/components/EmployeeDetail'
import { EmployeeForm } from '@/features/employees/components/EmployeeForm'
import { Dashboard } from '@/features/dashboard/components/Dashboard'
import { ContractList } from '@/features/contracts/components/ContractList'
import { ContractDetail } from '@/features/contracts/components/ContractDetail'
import { ContractForm } from '@/features/contracts/components/ContractForm'
import { CompensationList } from '@/features/compensation/components/CompensationList'
import { RateDetail } from '@/features/compensation/components/RateDetail'
import { BonusDetail } from '@/features/compensation/components/BonusDetail'
import { RateForm } from '@/features/compensation/components/RateForm'
import { BonusForm } from '@/features/compensation/components/BonusForm'
import { AbsenceList } from '@/features/absences/components/AbsenceList'
import { AbsenceDetail } from '@/features/absences/components/AbsenceDetail'
import { AbsenceForm } from '@/features/absences/components/AbsenceForm'
import { TimesheetList } from '@/features/timesheets/components/TimesheetList'
import { TimesheetDetail } from '@/features/timesheets/components/TimesheetDetail'
import { TimesheetForm } from '@/features/timesheets/components/TimesheetForm'
import { PayrollList } from '@/features/payroll/components/PayrollList'
import { PayrollDetail } from '@/features/payroll/components/PayrollDetail'
import { PayrollForm } from '@/features/payroll/components/PayrollForm'
import { ReportsList } from '@/features/reporting/components/ReportsList'
import { ReportDetail } from '@/features/reporting/components/ReportDetail'
import { CreateReportForm } from '@/features/reporting/components/CreateReportForm'
import { AuditList } from '@/features/audit/components/AuditList'
import { AuditDetail } from '@/features/audit/components/AuditDetail'
const Unauthorized = () => (
  <div className="flex min-h-screen items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold">403</h1>
      <p className="mt-2 text-gray-600">
        Unauthorized - You don't have permission to access this page
      </p>
    </div>
  </div>
)

const NotFound = () => (
  <div className="flex min-h-screen items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="mt-2 text-gray-600">Page not found</p>
    </div>
  </div>
)

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginForm />,
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        path: '',
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: '',
        element: <AppLayout />,
        children: [
          {
            path: 'dashboard',
            element: <Dashboard />,
          },
          {
            path: 'employees',
            element: <EmployeeList />,
          },
          {
            path: 'employees/new',
            element: <EmployeeForm />,
          },
          {
            path: 'employees/:id/edit',
            element: <EmployeeForm />,
          },
          {
            path: 'employees/:id',
            element: <EmployeeDetail />,
          },
          {
            path: 'contracts',
            element: <ContractList />,
          },
          {
            path: 'contracts/new',
            element: <ContractForm />,
          },
          {
            path: 'contracts/:id',
            element: <ContractDetail />,
          },
          {
            path: 'compensation',
            element: <CompensationList />,
          },
          {
            path: 'compensation/rates/new',
            element: <RateForm />,
          },
          {
            path: 'compensation/rates/:id',
            element: <RateDetail />,
          },
          {
            path: 'compensation/bonuses/new',
            element: <BonusForm />,
          },
          {
            path: 'compensation/bonuses/:id',
            element: <BonusDetail />,
          },
          {
            path: 'absences',
            element: <AbsenceList />,
          },
          {
            path: 'absences/new',
            element: <AbsenceForm />,
          },
          {
            path: 'absences/:id',
            element: <AbsenceDetail />,
          },
          {
            path: 'timesheets',
            element: <TimesheetList />,
          },
          {
            path: 'timesheets/new',
            element: <TimesheetForm />,
          },
          {
            path: 'timesheets/:id/edit',
            element: <TimesheetForm />,
          },
          {
            path: 'timesheets/:id',
            element: <TimesheetDetail />,
          },
          {
            path: 'payrolls',
            element: <PayrollList />,
          },
          {
            path: 'payrolls/new',
            element: <PayrollForm />,
          },
          {
            path: 'payrolls/:id',
            element: <PayrollDetail />,
          },
          {
            path: 'reports',
            element: <ReportsList />,
          },
          {
            path: 'reports/new',
            element: <CreateReportForm />,
          },
          {
            path: 'reports/:id',
            element: <ReportDetail />,
          },
          {
            path: 'audit',
            element: <AuditList />,
          },
          {
            path: 'audit/:id',
            element: <AuditDetail />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
