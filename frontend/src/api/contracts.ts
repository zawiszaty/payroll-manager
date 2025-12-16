import apiClient from './client'
import type {
  ContractDetailView,
  CreateContractRequest,
  CancelContractRequest,
  PaginatedResponse_ContractListView_,
  ContractListResponse,
} from '@/api'

/**
 * Contracts API endpoints
 */
export const contractsApi = {
  /**
   * List all contracts with pagination
   */
  list: async (page = 1, limit = 100): Promise<PaginatedResponse_ContractListView_> => {
    const response = await apiClient.get<PaginatedResponse_ContractListView_>('/contracts/', {
      params: { page, limit },
    })
    return response.data
  },

  /**
   * Get contract by ID
   */
  getById: async (contractId: string): Promise<ContractDetailView> => {
    const response = await apiClient.get<ContractDetailView>(`/contracts/${contractId}`)
    return response.data
  },

  /**
   * Get contracts for an employee
   */
  getByEmployee: async (employeeId: string): Promise<ContractListResponse> => {
    const response = await apiClient.get<ContractListResponse>(`/contracts/employee/${employeeId}`)
    return response.data
  },

  /**
   * Get active contracts for an employee
   */
  getActiveByEmployee: async (employeeId: string): Promise<ContractListResponse> => {
    const response = await apiClient.get<ContractListResponse>(
      `/contracts/employee/${employeeId}/active`
    )
    return response.data
  },

  /**
   * Create a new contract
   */
  create: async (data: CreateContractRequest): Promise<ContractDetailView> => {
    const response = await apiClient.post<ContractDetailView>('/contracts/', data)
    return response.data
  },

  /**
   * Activate a contract
   */
  activate: async (contractId: string): Promise<ContractDetailView> => {
    const response = await apiClient.post<ContractDetailView>(`/contracts/${contractId}/activate`)
    return response.data
  },

  /**
   * Cancel a contract
   */
  cancel: async (contractId: string, data: CancelContractRequest): Promise<ContractDetailView> => {
    const response = await apiClient.post<ContractDetailView>(
      `/contracts/${contractId}/cancel`,
      data
    )
    return response.data
  },

  /**
   * Expire a contract
   */
  expire: async (contractId: string): Promise<ContractDetailView> => {
    const response = await apiClient.post<ContractDetailView>(`/contracts/${contractId}/expire`)
    return response.data
  },
}
