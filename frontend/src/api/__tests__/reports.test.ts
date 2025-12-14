import { describe, it, expect, vi, beforeEach } from 'vitest'
import { reportsApi } from '../reports'
import apiClient from '../client'

vi.mock('../client')

describe('reportsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should fetch reports list', async () => {
      const mockResponse = {
        items: [
          {
            id: '1',
            name: 'Test Report',
            report_type: 'payroll_summary',
            format: 'pdf',
            status: 'completed',
          },
        ],
        total: 1,
        page: 1,
        limit: 100,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await reportsApi.list()

      expect(apiClient.get).toHaveBeenCalledWith('/reporting/')
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

      await expect(reportsApi.list()).rejects.toThrow('Network error')
    })
  })

  describe('getById', () => {
    it('should fetch a single report', async () => {
      const mockReport = {
        id: '1',
        name: 'Test Report',
        report_type: 'payroll_summary',
        format: 'pdf',
        status: 'completed',
        parameters: {},
        file_path: '/path/to/file.pdf',
        error_message: null,
        created_at: '2024-01-01T00:00:00Z',
        completed_at: '2024-01-01T00:05:00Z',
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockReport })

      const result = await reportsApi.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/reporting/1')
      expect(result).toEqual(mockReport)
    })
  })

  describe('create', () => {
    it('should create a new report', async () => {
      const mockRequest = {
        name: 'New Report',
        report_type: 'payroll_summary',
        format: 'pdf',
      }
      const mockResponse = {
        id: '1',
        ...mockRequest,
        status: 'pending',
        parameters: {},
        file_path: null,
        error_message: null,
        created_at: '2024-01-01T00:00:00Z',
        completed_at: null,
      }
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse })

      const result = await reportsApi.create(mockRequest)

      expect(apiClient.post).toHaveBeenCalledWith('/reporting/', mockRequest)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getByStatus', () => {
    it('should fetch reports by status', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        limit: 100,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await reportsApi.getByStatus('completed')

      expect(apiClient.get).toHaveBeenCalledWith('/reporting/status/completed')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getByType', () => {
    it('should fetch reports by type', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        limit: 100,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await reportsApi.getByType('payroll_summary')

      expect(apiClient.get).toHaveBeenCalledWith('/reporting/type/payroll_summary')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('download', () => {
    it('should download a report', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/pdf' })
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockBlob })

      const result = await reportsApi.download('1')

      expect(apiClient.get).toHaveBeenCalledWith('/reporting/1/download', {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })
  })
})
