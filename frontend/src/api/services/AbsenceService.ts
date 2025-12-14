/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceBalanceCreate } from '../models/AbsenceBalanceCreate'
import type { AbsenceBalanceDetailResponse } from '../models/AbsenceBalanceDetailResponse'
import type { AbsenceBalanceListResponse } from '../models/AbsenceBalanceListResponse'
import type { AbsenceBalanceResponse } from '../models/AbsenceBalanceResponse'
import type { AbsenceBalanceUpdate } from '../models/AbsenceBalanceUpdate'
import type { AbsenceCreate } from '../models/AbsenceCreate'
import type { AbsenceListResponse } from '../models/AbsenceListResponse'
import type { AbsenceResponse } from '../models/AbsenceResponse'
import type { PaginatedResponse_AbsenceBalanceResponse_ } from '../models/PaginatedResponse_AbsenceBalanceResponse_'
import type { PaginatedResponse_AbsenceResponse_ } from '../models/PaginatedResponse_AbsenceResponse_'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class AbsenceService {
  /**
   * Create Absence
   * @param requestBody
   * @returns AbsenceResponse Successful Response
   * @throws ApiError
   */
  public static createAbsenceApiV1AbsenceAbsencesPost(
    requestBody: AbsenceCreate
  ): CancelablePromise<AbsenceResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/absence/absences/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Absences
   * @param page
   * @param limit
   * @returns PaginatedResponse_AbsenceResponse_ Successful Response
   * @throws ApiError
   */
  public static listAbsencesApiV1AbsenceAbsencesGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_AbsenceResponse_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/absences/',
      query: {
        page: page,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Absence
   * @param absenceId
   * @returns AbsenceResponse Successful Response
   * @throws ApiError
   */
  public static getAbsenceApiV1AbsenceAbsencesAbsenceIdGet(
    absenceId: string
  ): CancelablePromise<AbsenceResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/absences/{absence_id}',
      path: {
        absence_id: absenceId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Absences By Employee
   * @param employeeId
   * @returns AbsenceListResponse Successful Response
   * @throws ApiError
   */
  public static getAbsencesByEmployeeApiV1AbsenceAbsencesEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<AbsenceListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/absences/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Approve Absence
   * @param absenceId
   * @returns AbsenceResponse Successful Response
   * @throws ApiError
   */
  public static approveAbsenceApiV1AbsenceAbsencesAbsenceIdApprovePost(
    absenceId: string
  ): CancelablePromise<AbsenceResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/absence/absences/{absence_id}/approve',
      path: {
        absence_id: absenceId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Reject Absence
   * @param absenceId
   * @returns AbsenceResponse Successful Response
   * @throws ApiError
   */
  public static rejectAbsenceApiV1AbsenceAbsencesAbsenceIdRejectPost(
    absenceId: string
  ): CancelablePromise<AbsenceResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/absence/absences/{absence_id}/reject',
      path: {
        absence_id: absenceId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Cancel Absence
   * @param absenceId
   * @returns AbsenceResponse Successful Response
   * @throws ApiError
   */
  public static cancelAbsenceApiV1AbsenceAbsencesAbsenceIdCancelPost(
    absenceId: string
  ): CancelablePromise<AbsenceResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/absence/absences/{absence_id}/cancel',
      path: {
        absence_id: absenceId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Create Absence Balance
   * @param requestBody
   * @returns AbsenceBalanceDetailResponse Successful Response
   * @throws ApiError
   */
  public static createAbsenceBalanceApiV1AbsenceBalancesPost(
    requestBody: AbsenceBalanceCreate
  ): CancelablePromise<AbsenceBalanceDetailResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/absence/balances/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Absence Balances
   * @param page
   * @param limit
   * @returns PaginatedResponse_AbsenceBalanceResponse_ Successful Response
   * @throws ApiError
   */
  public static listAbsenceBalancesApiV1AbsenceBalancesGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_AbsenceBalanceResponse_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/balances/',
      query: {
        page: page,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Absence Balance
   * @param balanceId
   * @returns AbsenceBalanceResponse Successful Response
   * @throws ApiError
   */
  public static getAbsenceBalanceApiV1AbsenceBalancesBalanceIdGet(
    balanceId: string
  ): CancelablePromise<AbsenceBalanceResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/balances/{balance_id}',
      path: {
        balance_id: balanceId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Update Absence Balance
   * @param balanceId
   * @param requestBody
   * @returns AbsenceBalanceDetailResponse Successful Response
   * @throws ApiError
   */
  public static updateAbsenceBalanceApiV1AbsenceBalancesBalanceIdPatch(
    balanceId: string,
    requestBody: AbsenceBalanceUpdate
  ): CancelablePromise<AbsenceBalanceDetailResponse> {
    return __request(OpenAPI, {
      method: 'PATCH',
      url: '/api/v1/absence/balances/{balance_id}',
      path: {
        balance_id: balanceId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Absence Balances By Employee
   * @param employeeId
   * @returns AbsenceBalanceListResponse Successful Response
   * @throws ApiError
   */
  public static getAbsenceBalancesByEmployeeApiV1AbsenceBalancesEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<AbsenceBalanceListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/balances/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Absence Balances By Employee And Year
   * @param employeeId
   * @param year
   * @returns AbsenceBalanceListResponse Successful Response
   * @throws ApiError
   */
  public static getAbsenceBalancesByEmployeeAndYearApiV1AbsenceBalancesEmployeeEmployeeIdYearYearGet(
    employeeId: string,
    year: number
  ): CancelablePromise<AbsenceBalanceListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/absence/balances/employee/{employee_id}/year/{year}',
      path: {
        employee_id: employeeId,
        year: year,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
