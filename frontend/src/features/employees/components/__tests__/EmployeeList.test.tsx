import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { EmployeeList } from '../EmployeeList'
import { employeeApi } from '@/api/employees'
import { EmploymentStatus, EmploymentType } from '../../types'

vi.mock('@/api/employees')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('EmployeeList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(employeeApi.getEmployees).mockImplementation(() => new Promise(() => {}))

    render(<EmployeeList />, { wrapper: createWrapper() })

    expect(screen.getByText(/loading employees/i)).toBeInTheDocument()
  })

  it('should load and display employees with ID column', async () => {
    const mockEmployees = {
      items: [
        {
          id: '5fe067fb-5e84-4939-aa60-6b6eaa06cd2e',
          employee_number: 'EMP001',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          date_of_birth: '1990-01-01',
          employment_type: EmploymentType.FULL_TIME,
          hire_date: '2024-01-01',
          status: EmploymentStatus.ACTIVE,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      skip: 0,
      limit: 10,
    }
    vi.mocked(employeeApi.getEmployees).mockResolvedValue(mockEmployees)

    render(<EmployeeList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByText('EMP001')).toBeInTheDocument()
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('5fe067fb...')).toBeInTheDocument()
  })

  it('should render search input', async () => {
    const mockEmployees = {
      items: [],
      total: 0,
      skip: 0,
      limit: 10,
    }
    vi.mocked(employeeApi.getEmployees).mockResolvedValue(mockEmployees)

    render(<EmployeeList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText(/search by id, name, email, or employee number/i)
      ).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(
      /search by id, name, email, or employee number/i
    )
    expect(searchInput).toHaveValue('')
  })

  it('should handle errors gracefully', async () => {
    vi.mocked(employeeApi.getEmployees).mockRejectedValue(new Error('API Error'))

    render(<EmployeeList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/failed to load employees/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no employees', async () => {
    vi.mocked(employeeApi.getEmployees).mockResolvedValue({
      items: [],
      total: 0,
      skip: 0,
      limit: 10,
    })

    render(<EmployeeList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/no employees found/i)).toBeInTheDocument()
    })
  })
})
