/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangeStatusRequest } from '../models/ChangeStatusRequest'
import type { CreateEmployeeRequest } from '../models/CreateEmployeeRequest'
import type { EmployeeDetailView } from '../models/EmployeeDetailView'
import type { PaginatedResponse_EmployeeListView_ } from '../models/PaginatedResponse_EmployeeListView_'
import type { UpdateEmployeeRequest } from '../models/UpdateEmployeeRequest'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class EmployeesService {
  /**
   * Create Employee
   * @param requestBody
   * @returns EmployeeDetailView Successful Response
   * @throws ApiError
   */
  public static createEmployeeApiV1EmployeesPost(
    requestBody: CreateEmployeeRequest
  ): CancelablePromise<EmployeeDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/employees/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Employees
   * @param page
   * @param limit
   * @returns PaginatedResponse_EmployeeListView_ Successful Response
   * @throws ApiError
   */
  public static listEmployeesApiV1EmployeesGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_EmployeeListView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/employees/',
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
   * Get Employee
   * @param employeeId
   * @returns EmployeeDetailView Successful Response
   * @throws ApiError
   */
  public static getEmployeeApiV1EmployeesEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<EmployeeDetailView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/employees/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Update Employee
   * @param employeeId
   * @param requestBody
   * @returns EmployeeDetailView Successful Response
   * @throws ApiError
   */
  public static updateEmployeeApiV1EmployeesEmployeeIdPut(
    employeeId: string,
    requestBody: UpdateEmployeeRequest
  ): CancelablePromise<EmployeeDetailView> {
    return __request(OpenAPI, {
      method: 'PUT',
      url: '/api/v1/employees/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Change Employee Status
   * @param employeeId
   * @param requestBody
   * @returns EmployeeDetailView Successful Response
   * @throws ApiError
   */
  public static changeEmployeeStatusApiV1EmployeesEmployeeIdStatusPost(
    employeeId: string,
    requestBody: ChangeStatusRequest
  ): CancelablePromise<EmployeeDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/employees/{employee_id}/status',
      path: {
        employee_id: employeeId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
