import apiClient from './client'
import type {
  Timesheet,
  CreateTimesheetRequest,
  UpdateTimesheetRequest,
  ApproveTimesheetRequest,
  RejectTimesheetRequest,
  HoursSummaryResponse,
} from '@/features/timesheets/types'

export const timesheetApi = {
  list: async (): Promise<Timesheet[]> => {
    const response = await apiClient.get<Timesheet[]>('/timesheets/')
    return response.data
  },

  getById: async (id: string): Promise<Timesheet> => {
    const response = await apiClient.get<Timesheet>(`/timesheets/${id}`)
    return response.data
  },

  getByEmployee: async (employeeId: string): Promise<Timesheet[]> => {
    const response = await apiClient.get<Timesheet[]>(`/timesheets/employee/${employeeId}`)
    return response.data
  },

  getByEmployeeAndPeriod: async (
    employeeId: string,
    startDate: string,
    endDate: string
  ): Promise<Timesheet[]> => {
    const response = await apiClient.get<Timesheet[]>(`/timesheets/employee/${employeeId}/period`, {
      params: { start_date: startDate, end_date: endDate },
    })
    return response.data
  },

  getByStatus: async (status: string): Promise<Timesheet[]> => {
    const response = await apiClient.get<Timesheet[]>(`/timesheets/status/${status}`)
    return response.data
  },

  getPendingApproval: async (): Promise<Timesheet[]> => {
    const response = await apiClient.get<Timesheet[]>('/timesheets/pending-approval/list')
    return response.data
  },

  getHoursSummary: async (
    employeeId: string,
    startDate: string,
    endDate: string
  ): Promise<HoursSummaryResponse> => {
    const response = await apiClient.get<HoursSummaryResponse>(
      `/timesheets/employee/${employeeId}/hours-summary`,
      {
        params: { start_date: startDate, end_date: endDate },
      }
    )
    return response.data
  },

  create: async (data: CreateTimesheetRequest): Promise<Timesheet> => {
    const response = await apiClient.post<Timesheet>('/timesheets/', data)
    return response.data
  },

  update: async (id: string, data: UpdateTimesheetRequest): Promise<Timesheet> => {
    const response = await apiClient.put<Timesheet>(`/timesheets/${id}`, data)
    return response.data
  },

  submit: async (id: string): Promise<Timesheet> => {
    const response = await apiClient.post<Timesheet>(`/timesheets/${id}/submit`)
    return response.data
  },

  approve: async (id: string, data: ApproveTimesheetRequest): Promise<Timesheet> => {
    const response = await apiClient.post<Timesheet>(`/timesheets/${id}/approve`, data)
    return response.data
  },

  reject: async (id: string, data: RejectTimesheetRequest): Promise<Timesheet> => {
    const response = await apiClient.post<Timesheet>(`/timesheets/${id}/reject`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/timesheets/${id}`)
  },
}
