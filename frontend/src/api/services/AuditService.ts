/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuditLogListResponse } from '../models/AuditLogListResponse'
import type { AuditLogResponse } from '../models/AuditLogResponse'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class AuditService {
  /**
   * List Audit Logs
   * @param page
   * @param limit
   * @param entityType
   * @param action
   * @returns AuditLogListResponse Successful Response
   * @throws ApiError
   */
  public static listAuditLogsApiV1AuditGet(
    page: number = 1,
    limit: number = 100,
    entityType?: string | null,
    action?: string | null
  ): CancelablePromise<AuditLogListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/audit/',
      query: {
        page: page,
        limit: limit,
        entity_type: entityType,
        action: action,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Audit Logs By Entity
   * @param entityType
   * @param entityId
   * @param page
   * @param limit
   * @returns AuditLogListResponse Successful Response
   * @throws ApiError
   */
  public static getAuditLogsByEntityApiV1AuditEntityEntityTypeEntityIdGet(
    entityType: string,
    entityId: string,
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<AuditLogListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/audit/entity/{entity_type}/{entity_id}',
      path: {
        entity_type: entityType,
        entity_id: entityId,
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
   * Get Audit Logs By Employee
   * @param employeeId
   * @param page
   * @param limit
   * @returns AuditLogListResponse Successful Response
   * @throws ApiError
   */
  public static getAuditLogsByEmployeeApiV1AuditEmployeeEmployeeIdGet(
    employeeId: string,
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<AuditLogListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/audit/employee/{employee_id}',
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
   * Get Audit Timeline
   * @param page
   * @param limit
   * @param entityType
   * @param employeeId
   * @param dateFrom
   * @param dateTo
   * @returns AuditLogListResponse Successful Response
   * @throws ApiError
   */
  public static getAuditTimelineApiV1AuditTimelineGet(
    page: number = 1,
    limit: number = 100,
    entityType?: string | null,
    employeeId?: string | null,
    dateFrom?: string | null,
    dateTo?: string | null
  ): CancelablePromise<AuditLogListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/audit/timeline',
      query: {
        page: page,
        limit: limit,
        entity_type: entityType,
        employee_id: employeeId,
        date_from: dateFrom,
        date_to: dateTo,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Audit Log
   * @param auditId
   * @returns AuditLogResponse Successful Response
   * @throws ApiError
   */
  public static getAuditLogApiV1AuditAuditIdGet(
    auditId: string
  ): CancelablePromise<AuditLogResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/audit/{audit_id}',
      path: {
        audit_id: auditId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
