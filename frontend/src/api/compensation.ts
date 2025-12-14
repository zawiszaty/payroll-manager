import apiClient from './client'
import type {
  RateView,
  BonusView,
  CreateRateRequest,
  CreateBonusRequest,
  PaginatedResponse_RateView_,
  PaginatedResponse_BonusView_,
  RateListResponse,
  BonusListResponse,
} from '@/lib/api'

export const compensationApi = {
  rates: {
    list: async (page = 1, limit = 100): Promise<PaginatedResponse_RateView_> => {
      const response = await apiClient.get<PaginatedResponse_RateView_>('/compensation/rates/', {
        params: { page, limit },
      })
      return response.data
    },

    getById: async (rateId: string): Promise<RateView> => {
      const response = await apiClient.get<RateView>(`/compensation/rates/${rateId}`)
      return response.data
    },

    getByEmployee: async (employeeId: string): Promise<RateListResponse> => {
      const response = await apiClient.get<RateListResponse>(
        `/compensation/rates/employee/${employeeId}`
      )
      return response.data
    },

    getActiveByEmployee: async (employeeId: string, checkDate?: string): Promise<RateView> => {
      const response = await apiClient.get<RateView>(
        `/compensation/rates/employee/${employeeId}/active`,
        {
          params: checkDate ? { check_date: checkDate } : {},
        }
      )
      return response.data
    },

    create: async (data: CreateRateRequest): Promise<RateView> => {
      const response = await apiClient.post<RateView>('/compensation/rates/', data)
      return response.data
    },
  },

  bonuses: {
    list: async (page = 1, limit = 100): Promise<PaginatedResponse_BonusView_> => {
      const response = await apiClient.get<PaginatedResponse_BonusView_>('/compensation/bonuses/', {
        params: { page, limit },
      })
      return response.data
    },

    getById: async (bonusId: string): Promise<BonusView> => {
      const response = await apiClient.get<BonusView>(`/compensation/bonuses/${bonusId}`)
      return response.data
    },

    getByEmployee: async (employeeId: string): Promise<BonusListResponse> => {
      const response = await apiClient.get<BonusListResponse>(
        `/compensation/bonuses/employee/${employeeId}`
      )
      return response.data
    },

    create: async (data: CreateBonusRequest): Promise<BonusView> => {
      const response = await apiClient.post<BonusView>('/compensation/bonuses/', data)
      return response.data
    },
  },
}
