import { describe, it, expect, vi, beforeEach } from 'vitest'
import { compensationApi } from '../compensation'
import apiClient from '../client'

vi.mock('../client')

describe('compensationApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rates', () => {
    describe('list', () => {
      it('should fetch rates with default pagination', async () => {
        const mockResponse = {
          items: [],
          total: 0,
          page: 1,
          limit: 100,
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

        const result = await compensationApi.rates.list()

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/rates/', {
          params: { page: 1, limit: 100 },
        })
        expect(result).toEqual(mockResponse)
      })

      it('should handle API errors', async () => {
        vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

        await expect(compensationApi.rates.list()).rejects.toThrow('Network error')
      })
    })

    describe('getById', () => {
      it('should fetch rate by ID', async () => {
        const mockRate = {
          id: 'rate-1',
          employee_id: 'emp-1',
          rate_type: 'base_salary',
          amount: '5000',
          currency: 'USD',
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockRate })

        const result = await compensationApi.rates.getById('rate-1')

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/rates/rate-1')
        expect(result).toEqual(mockRate)
      })
    })

    describe('getByEmployee', () => {
      it('should fetch rates for an employee', async () => {
        const mockRates = {
          items: [],
          total: 0,
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockRates })

        const result = await compensationApi.rates.getByEmployee('emp-1')

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/rates/employee/emp-1')
        expect(result).toEqual(mockRates)
      })
    })

    describe('create', () => {
      it('should create a new rate', async () => {
        const mockRate = {
          employee_id: 'emp-1',
          rate_type: 'base_salary',
          amount: 5000,
          currency: 'USD',
          valid_from: '2024-01-01',
        }
        vi.mocked(apiClient.post).mockResolvedValue({ data: mockRate })

        const result = await compensationApi.rates.create(mockRate as any)

        expect(apiClient.post).toHaveBeenCalledWith('/compensation/rates/', mockRate)
        expect(result).toEqual(mockRate)
      })
    })
  })

  describe('bonuses', () => {
    describe('list', () => {
      it('should fetch bonuses with default pagination', async () => {
        const mockResponse = {
          items: [],
          total: 0,
          page: 1,
          limit: 100,
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

        const result = await compensationApi.bonuses.list()

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/bonuses/', {
          params: { page: 1, limit: 100 },
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('getById', () => {
      it('should fetch bonus by ID', async () => {
        const mockBonus = {
          id: 'bonus-1',
          employee_id: 'emp-1',
          bonus_type: 'performance',
          amount: '1000',
          currency: 'USD',
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockBonus })

        const result = await compensationApi.bonuses.getById('bonus-1')

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/bonuses/bonus-1')
        expect(result).toEqual(mockBonus)
      })
    })

    describe('getByEmployee', () => {
      it('should fetch bonuses for an employee', async () => {
        const mockBonuses = {
          items: [],
          total: 0,
        }
        vi.mocked(apiClient.get).mockResolvedValue({ data: mockBonuses })

        const result = await compensationApi.bonuses.getByEmployee('emp-1')

        expect(apiClient.get).toHaveBeenCalledWith('/compensation/bonuses/employee/emp-1')
        expect(result).toEqual(mockBonuses)
      })
    })

    describe('create', () => {
      it('should create a new bonus', async () => {
        const mockBonus = {
          employee_id: 'emp-1',
          bonus_type: 'performance',
          amount: 1000,
          currency: 'USD',
          payment_date: '2024-01-15',
        }
        vi.mocked(apiClient.post).mockResolvedValue({ data: mockBonus })

        const result = await compensationApi.bonuses.create(mockBonus as any)

        expect(apiClient.post).toHaveBeenCalledWith('/compensation/bonuses/', mockBonus)
        expect(result).toEqual(mockBonus)
      })
    })
  })
})
