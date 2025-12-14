import { describe, it, expect, vi, beforeEach } from 'vitest'
import { auditApi } from '../audit'
import apiClient from '../client'

vi.mock('../client')

describe('auditApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should fetch audit logs with default pagination', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        limit: 100,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await auditApi.list()

      expect(apiClient.get).toHaveBeenCalledWith('/audit/', {
        params: {
          page: 1,
          limit: 100,
          entity_type: undefined,
          action: undefined,
        },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should fetch audit logs with custom parameters', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 2,
        limit: 50,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      await auditApi.list({
        page: 2,
        limit: 50,
        entity_type: 'employee',
        action: 'created',
      })

      expect(apiClient.get).toHaveBeenCalledWith('/audit/', {
        params: {
          page: 2,
          limit: 50,
          entity_type: 'employee',
          action: 'created',
        },
      })
    })

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

      await expect(auditApi.list()).rejects.toThrow('Network error')
    })
  })

  describe('getById', () => {
    it('should fetch a single audit log', async () => {
      const mockAuditLog = {
        id: '1',
        entity_type: 'employee',
        entity_id: 'emp-1',
        employee_id: 'emp-1',
        action: 'created',
        old_values: null,
        new_values: { name: 'John Doe' },
        changed_by: 'user-1',
        metadata: {},
        occurred_at: '2024-01-01T00:00:00Z',
        created_at: '2024-01-01T00:00:00Z',
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockAuditLog })

      const result = await auditApi.getById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/audit/1')
      expect(result).toEqual(mockAuditLog)
    })
  })

  describe('getByEntity', () => {
    it('should fetch audit logs for a specific entity', async () => {
      const mockResponse = {
        items: [
          {
            id: '1',
            entity_type: 'employee',
            entity_id: 'emp-1',
            employee_id: 'emp-1',
            action: 'created',
            old_values: null,
            new_values: {},
            changed_by: 'user-1',
            metadata: {},
            occurred_at: '2024-01-01T00:00:00Z',
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 1,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await auditApi.getByEntity('employee', 'emp-1')

      expect(apiClient.get).toHaveBeenCalledWith('/audit/entity/employee/emp-1')
      expect(result).toEqual(mockResponse.items)
    })
  })

  describe('getByEmployee', () => {
    it('should fetch audit logs for a specific employee', async () => {
      const mockResponse = {
        items: [],
        total: 0,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await auditApi.getByEmployee('emp-1')

      expect(apiClient.get).toHaveBeenCalledWith('/audit/employee/emp-1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getTimeline', () => {
    it('should fetch audit timeline', async () => {
      const mockResponse = {
        items: [],
        total: 0,
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      await auditApi.getTimeline({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        entity_type: 'employee',
      })

      expect(apiClient.get).toHaveBeenCalledWith('/audit/timeline', {
        params: {
          start_date: '2024-01-01',
          end_date: '2024-01-31',
          entity_type: 'employee',
        },
      })
    })
  })
})
