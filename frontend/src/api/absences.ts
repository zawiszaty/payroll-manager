import apiClient from './client'
import type {
  Absence,
  AbsenceBalance,
  CreateAbsenceRequest,
  CreateBalanceRequest,
  UpdateBalanceRequest,
  AbsenceListResponse,
  AbsenceBalanceListResponse,
} from '@/features/absences/types'

export const absencesApi = {
  list: async (page: number = 1, limit: number = 100): Promise<AbsenceListResponse> => {
    const response = await apiClient.get<AbsenceListResponse>('/absence/absences/', {
      params: { page, limit },
    })
    return response.data
  },

  getById: async (id: string): Promise<Absence> => {
    const response = await apiClient.get<Absence>(`/absence/absences/${id}`)
    return response.data
  },

  create: async (data: CreateAbsenceRequest): Promise<Absence> => {
    const response = await apiClient.post<Absence>('/absence/absences/', data)
    return response.data
  },

  getByEmployee: async (employeeId: string): Promise<AbsenceListResponse> => {
    const response = await apiClient.get<AbsenceListResponse>(
      `/absence/absences/employee/${employeeId}`
    )
    return response.data
  },

  approve: async (id: string): Promise<Absence> => {
    const response = await apiClient.post<Absence>(`/absence/absences/${id}/approve`)
    return response.data
  },

  reject: async (id: string): Promise<Absence> => {
    const response = await apiClient.post<Absence>(`/absence/absences/${id}/reject`)
    return response.data
  },

  cancel: async (id: string): Promise<Absence> => {
    const response = await apiClient.post<Absence>(`/absence/absences/${id}/cancel`)
    return response.data
  },
}

export const balancesApi = {
  list: async (page: number = 1, limit: number = 100): Promise<AbsenceBalanceListResponse> => {
    const response = await apiClient.get<AbsenceBalanceListResponse>('/absence/balances/', {
      params: { page, limit },
    })
    return response.data
  },

  getById: async (id: string): Promise<AbsenceBalance> => {
    const response = await apiClient.get<AbsenceBalance>(`/absence/balances/${id}`)
    return response.data
  },

  create: async (data: CreateBalanceRequest): Promise<AbsenceBalance> => {
    const response = await apiClient.post<AbsenceBalance>('/absence/balances/', data)
    return response.data
  },

  getByEmployee: async (employeeId: string): Promise<AbsenceBalanceListResponse> => {
    const response = await apiClient.get<AbsenceBalanceListResponse>(
      `/absence/balances/employee/${employeeId}`
    )
    return response.data
  },

  getByEmployeeAndYear: async (
    employeeId: string,
    year: number
  ): Promise<AbsenceBalanceListResponse> => {
    const response = await apiClient.get<AbsenceBalanceListResponse>(
      `/absence/balances/employee/${employeeId}/year/${year}`
    )
    return response.data
  },

  update: async (id: string, data: UpdateBalanceRequest): Promise<AbsenceBalance> => {
    const response = await apiClient.patch<AbsenceBalance>(`/absence/balances/${id}`, data)
    return response.data
  },
}
