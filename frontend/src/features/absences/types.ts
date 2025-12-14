export enum AbsenceType {
  VACATION = 'vacation',
  SICK_LEAVE = 'sick_leave',
  PARENTAL_LEAVE = 'parental_leave',
  UNPAID_LEAVE = 'unpaid_leave',
  BEREAVEMENT = 'bereavement',
  STUDY_LEAVE = 'study_leave',
  COMPASSIONATE = 'compassionate',
}

export enum AbsenceStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
}

export interface Absence {
  id: string
  employee_id: string
  absence_type: AbsenceType
  start_date: string
  end_date: string
  status: AbsenceStatus
  reason?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface AbsenceBalance {
  id: string
  employee_id: string
  absence_type: AbsenceType
  year: number
  total_days: number
  used_days: number
  remaining_days: number
}

export interface CreateAbsenceRequest {
  employee_id: string
  absence_type: AbsenceType
  start_date: string
  end_date: string
  reason?: string
  notes?: string
}

export interface CreateBalanceRequest {
  employee_id: string
  absence_type: AbsenceType
  year: number
  total_days: number
}

export interface UpdateBalanceRequest {
  total_days: number
}

export interface AbsenceListResponse {
  items: Absence[]
  total: number
}

export interface AbsenceBalanceListResponse {
  items: AbsenceBalance[]
  total: number
}

export const ABSENCE_TYPE_LABELS: Record<AbsenceType, string> = {
  [AbsenceType.VACATION]: 'Vacation',
  [AbsenceType.SICK_LEAVE]: 'Sick Leave',
  [AbsenceType.PARENTAL_LEAVE]: 'Parental Leave',
  [AbsenceType.UNPAID_LEAVE]: 'Unpaid Leave',
  [AbsenceType.BEREAVEMENT]: 'Bereavement',
  [AbsenceType.STUDY_LEAVE]: 'Study Leave',
  [AbsenceType.COMPASSIONATE]: 'Compassionate',
}

export const ABSENCE_STATUS_LABELS: Record<AbsenceStatus, string> = {
  [AbsenceStatus.PENDING]: 'Pending',
  [AbsenceStatus.APPROVED]: 'Approved',
  [AbsenceStatus.REJECTED]: 'Rejected',
  [AbsenceStatus.CANCELLED]: 'Cancelled',
}

export const ABSENCE_STATUS_COLORS: Record<AbsenceStatus, string> = {
  [AbsenceStatus.PENDING]: 'bg-yellow-100 text-yellow-800',
  [AbsenceStatus.APPROVED]: 'bg-green-100 text-green-800',
  [AbsenceStatus.REJECTED]: 'bg-red-100 text-red-800',
  [AbsenceStatus.CANCELLED]: 'bg-gray-100 text-gray-800',
}
