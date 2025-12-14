import { describe, it, expect, vi, beforeEach } from 'vitest'
import { absencesApi } from '../absences'
import apiClient from '../client'

vi.mock('../client')

describe('absencesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should fetch absences with default pagination', async () => {
      const mockResponse = {
        items: [],
        total: 0,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await absencesApi.list()

      expect(apiClient.get).toHaveBeenCalledWith('/absence/absences/', {
        params: { page: 1, limit: 100 },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

      await expect(absencesApi.list()).rejects.toThrow('Network error')
    })
  })

  describe('getById', () => {
    it('should fetch a single absence', async () => {
      const mockAbsence = {
        id: '1',
        employee_id: 'emp-1',
        absence_type: 'vacation',
        start_date: '2024-01-01',
        end_date: '2024-01-05',
        status: 'pending',
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAbsence })

      const result = await absencesApi.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/absence/absences/1')
      expect(result).toEqual(mockAbsence)
    })
  })

  describe('create', () => {
    it('should create a new absence', async () => {
      const mockRequest = {
        employee_id: 'emp-1',
        absence_type: 'vacation' as const,
        start_date: '2024-01-01',
        end_date: '2024-01-05',
      }
      const mockResponse = {
        id: '1',
        ...mockRequest,
        status: 'pending' as const,
      }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await absencesApi.create(mockRequest)

      expect(apiClient.post).toHaveBeenCalledWith('/absence/absences/', mockRequest)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('approve', () => {
    it('should approve an absence', async () => {
      const mockResponse = {
        id: '1',
        status: 'approved',
      }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await absencesApi.approve('1')

      expect(apiClient.post).toHaveBeenCalledWith('/absence/absences/1/approve')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('reject', () => {
    it('should reject an absence', async () => {
      const mockResponse = {
        id: '1',
        status: 'rejected',
      }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await absencesApi.reject('1')

      expect(apiClient.post).toHaveBeenCalledWith('/absence/absences/1/reject')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('cancel', () => {
    it('should cancel an absence', async () => {
      const mockResponse = {
        id: '1',
        status: 'cancelled',
      }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await absencesApi.cancel('1')

      expect(apiClient.post).toHaveBeenCalledWith('/absence/absences/1/cancel')
      expect(result).toEqual(mockResponse)
    })
  })
})
