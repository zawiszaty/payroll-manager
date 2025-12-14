/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BonusListResponse } from '../models/BonusListResponse'
import type { BonusView } from '../models/BonusView'
import type { CreateBonusRequest } from '../models/CreateBonusRequest'
import type { CreateRateRequest } from '../models/CreateRateRequest'
import type { PaginatedResponse_BonusView_ } from '../models/PaginatedResponse_BonusView_'
import type { PaginatedResponse_RateView_ } from '../models/PaginatedResponse_RateView_'
import type { RateListResponse } from '../models/RateListResponse'
import type { RateView } from '../models/RateView'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class CompensationService {
  /**
   * Create Rate
   * @param requestBody
   * @returns RateView Successful Response
   * @throws ApiError
   */
  public static createRateApiV1CompensationRatesPost(
    requestBody: CreateRateRequest
  ): CancelablePromise<RateView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/compensation/rates/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Rates
   * @param page
   * @param limit
   * @returns PaginatedResponse_RateView_ Successful Response
   * @throws ApiError
   */
  public static listRatesApiV1CompensationRatesGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_RateView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/rates/',
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
   * Get Rate
   * @param rateId
   * @returns RateView Successful Response
   * @throws ApiError
   */
  public static getRateApiV1CompensationRatesRateIdGet(
    rateId: string
  ): CancelablePromise<RateView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/rates/{rate_id}',
      path: {
        rate_id: rateId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Rates By Employee
   * @param employeeId
   * @returns RateListResponse Successful Response
   * @throws ApiError
   */
  public static getRatesByEmployeeApiV1CompensationRatesEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<RateListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/rates/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Active Rate
   * @param employeeId
   * @param checkDate
   * @returns RateView Successful Response
   * @throws ApiError
   */
  public static getActiveRateApiV1CompensationRatesEmployeeEmployeeIdActiveGet(
    employeeId: string,
    checkDate: string = '2025-12-13'
  ): CancelablePromise<RateView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/rates/employee/{employee_id}/active',
      path: {
        employee_id: employeeId,
      },
      query: {
        check_date: checkDate,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Create Bonus
   * @param requestBody
   * @returns BonusView Successful Response
   * @throws ApiError
   */
  public static createBonusApiV1CompensationBonusesPost(
    requestBody: CreateBonusRequest
  ): CancelablePromise<BonusView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/compensation/bonuses/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Bonuses
   * @param page
   * @param limit
   * @returns PaginatedResponse_BonusView_ Successful Response
   * @throws ApiError
   */
  public static listBonusesApiV1CompensationBonusesGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_BonusView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/bonuses/',
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
   * Get Bonus
   * @param bonusId
   * @returns BonusView Successful Response
   * @throws ApiError
   */
  public static getBonusApiV1CompensationBonusesBonusIdGet(
    bonusId: string
  ): CancelablePromise<BonusView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/bonuses/{bonus_id}',
      path: {
        bonus_id: bonusId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Bonuses By Employee
   * @param employeeId
   * @returns BonusListResponse Successful Response
   * @throws ApiError
   */
  public static getBonusesByEmployeeApiV1CompensationBonusesEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<BonusListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/compensation/bonuses/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
