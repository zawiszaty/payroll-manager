import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  FileText,
  DollarSign,
  Calendar,
  Clock,
  Briefcase,
  BarChart,
  Shield,
} from 'lucide-react'
import { useAppSelector } from '@/store/hooks'
import { UserRole } from '@/features/auth/types'
import { cn } from '@/lib/utils'

interface NavItem {
  name: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  allowedRoles?: UserRole[]
}

const navItems: NavItem[] = [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Employees',
    path: '/employees',
    icon: Users,
  },
  {
    name: 'Contracts',
    path: '/contracts',
    icon: FileText,
  },
  {
    name: 'Compensation',
    path: '/compensation',
    icon: DollarSign,
  },
  {
    name: 'Absences',
    path: '/absences',
    icon: Calendar,
  },
  {
    name: 'Timesheets',
    path: '/timesheets',
    icon: Clock,
  },
  {
    name: 'Payrolls',
    path: '/payrolls',
    icon: Briefcase,
  },
  {
    name: 'Reports',
    path: '/reports',
    icon: BarChart,
  },
  {
    name: 'Audit',
    path: '/audit',
    icon: Shield,
    allowedRoles: [UserRole.ADMIN],
  },
]

export function Sidebar() {
  const { user } = useAppSelector((state) => state.auth)

  const filteredNavItems = navItems.filter((item) => {
    if (!item.allowedRoles) return true
    return user && item.allowedRoles.includes(user.role)
  })

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="flex h-16 items-center border-b border-gray-200 px-6 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Payroll Manager</h1>
      </div>

      <nav className="space-y-1 p-4">
        {filteredNavItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                )
              }
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}
