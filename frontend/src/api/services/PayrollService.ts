/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovePayrollRequest } from '../models/ApprovePayrollRequest'
import type { CalculatePayrollRequest } from '../models/CalculatePayrollRequest'
import type { CreatePayrollRequest } from '../models/CreatePayrollRequest'
import type { MarkAsPaidRequest } from '../models/MarkAsPaidRequest'
import type { PaginatedResponse_PayrollListView_ } from '../models/PaginatedResponse_PayrollListView_'
import type { PayrollDetailView } from '../models/PayrollDetailView'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class PayrollService {
  /**
   * Create Payroll
   * @param requestBody
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static createPayrollApiV1PayrollPost(
    requestBody: CreatePayrollRequest
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/payroll/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Payrolls
   * @param page
   * @param limit
   * @returns PaginatedResponse_PayrollListView_ Successful Response
   * @throws ApiError
   */
  public static listPayrollsApiV1PayrollGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_PayrollListView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/payroll/',
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
   * Get Payroll
   * @param payrollId
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static getPayrollApiV1PayrollPayrollIdGet(
    payrollId: string
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/payroll/{payroll_id}',
      path: {
        payroll_id: payrollId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Payrolls By Employee
   * @param employeeId
   * @param page
   * @param limit
   * @returns PaginatedResponse_PayrollListView_ Successful Response
   * @throws ApiError
   */
  public static listPayrollsByEmployeeApiV1PayrollEmployeeEmployeeIdGet(
    employeeId: string,
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_PayrollListView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/payroll/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
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
   * Calculate Payroll
   * @param payrollId
   * @param requestBody
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static calculatePayrollApiV1PayrollPayrollIdCalculatePost(
    payrollId: string,
    requestBody: CalculatePayrollRequest
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/payroll/{payroll_id}/calculate',
      path: {
        payroll_id: payrollId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Approve Payroll
   * @param payrollId
   * @param requestBody
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static approvePayrollApiV1PayrollPayrollIdApprovePost(
    payrollId: string,
    requestBody: ApprovePayrollRequest
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/payroll/{payroll_id}/approve',
      path: {
        payroll_id: payrollId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Process Payroll
   * @param payrollId
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static processPayrollApiV1PayrollPayrollIdProcessPost(
    payrollId: string
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/payroll/{payroll_id}/process',
      path: {
        payroll_id: payrollId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Mark Payroll As Paid
   * @param payrollId
   * @param requestBody
   * @returns PayrollDetailView Successful Response
   * @throws ApiError
   */
  public static markPayrollAsPaidApiV1PayrollPayrollIdMarkPaidPost(
    payrollId: string,
    requestBody: MarkAsPaidRequest
  ): CancelablePromise<PayrollDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/payroll/{payroll_id}/mark-paid',
      path: {
        payroll_id: payrollId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
