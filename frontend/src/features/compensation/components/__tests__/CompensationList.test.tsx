import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { CompensationList } from '../CompensationList'
import { compensationApi } from '@/api/compensation'
import apiClient from '@/api/client'

vi.mock('@/api/compensation')
vi.mock('@/api/client')

describe('CompensationList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    vi.mocked(compensationApi.rates.list).mockImplementation(() => new Promise(() => {}))
    vi.mocked(compensationApi.bonuses.list).mockImplementation(() => new Promise(() => {}))
    vi.mocked(apiClient.get).mockImplementation(() => new Promise(() => {}))

    render(
      <MemoryRouter>
        <CompensationList />
      </MemoryRouter>
    )

    expect(screen.getByText(/loading compensation data/i)).toBeInTheDocument()
  })

  it('should load and display rates and bonuses', async () => {
    const mockRates = [
      {
        id: 'rate-1',
        employee_id: 'emp-1',
        rate_type: 'base_salary',
        amount: '5000',
        currency: 'USD',
        valid_from: '2024-01-01',
        valid_to: null,
      },
    ]

    const mockBonuses = [
      {
        id: 'bonus-1',
        employee_id: 'emp-1',
        bonus_type: 'performance',
        amount: '1000',
        currency: 'USD',
        payment_date: '2024-01-15',
      },
    ]

    const mockEmployees = [
      {
        id: 'emp-1',
        first_name: 'John',
        last_name: 'Doe',
      },
    ]

    vi.mocked(compensationApi.rates.list).mockResolvedValue({
      items: mockRates,
      total: 1,
      page: 1,
      limit: 100,
    } as any)

    vi.mocked(compensationApi.bonuses.list).mockResolvedValue({
      items: mockBonuses,
      total: 1,
      page: 1,
      limit: 100,
    } as any)

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { items: mockEmployees },
    } as any)

    render(
      <MemoryRouter>
        <CompensationList />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Compensation')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('Base Salary')).toBeInTheDocument()
    })
  })

  it('should handle errors gracefully', async () => {
    vi.mocked(compensationApi.rates.list).mockRejectedValue(new Error('API Error'))
    vi.mocked(compensationApi.bonuses.list).mockRejectedValue(new Error('API Error'))
    vi.mocked(apiClient.get).mockRejectedValue(new Error('API Error'))

    render(
      <MemoryRouter>
        <CompensationList />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/failed to load compensation data/i)).toBeInTheDocument()
    })
  })

  it('should display empty state when no data', async () => {
    vi.mocked(compensationApi.rates.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 100,
    } as any)

    vi.mocked(compensationApi.bonuses.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 100,
    } as any)

    vi.mocked(apiClient.get).mockResolvedValue({
      data: { items: [] },
    } as any)

    render(
      <MemoryRouter>
        <CompensationList />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Compensation')).toBeInTheDocument()
    })
  })
})
