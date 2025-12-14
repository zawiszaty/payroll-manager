/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateReportRequest } from '../models/CreateReportRequest'
import type { ReportListResponse } from '../models/ReportListResponse'
import type { ReportResponse } from '../models/ReportResponse'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class ReportingService {
  /**
   * List Reports
   * @returns ReportListResponse Successful Response
   * @throws ApiError
   */
  public static listReportsApiV1ReportingGet(): CancelablePromise<ReportListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/reporting/',
    })
  }
  /**
   * Create Report
   * @param requestBody
   * @returns ReportResponse Successful Response
   * @throws ApiError
   */
  public static createReportApiV1ReportingPost(
    requestBody: CreateReportRequest
  ): CancelablePromise<ReportResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/reporting/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Report
   * @param reportId
   * @returns ReportResponse Successful Response
   * @throws ApiError
   */
  public static getReportApiV1ReportingReportIdGet(
    reportId: string
  ): CancelablePromise<ReportResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/reporting/{report_id}',
      path: {
        report_id: reportId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Delete Report
   * @param reportId
   * @returns void
   * @throws ApiError
   */
  public static deleteReportApiV1ReportingReportIdDelete(
    reportId: string
  ): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/api/v1/reporting/{report_id}',
      path: {
        report_id: reportId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Reports By Type
   * @param reportType
   * @returns ReportListResponse Successful Response
   * @throws ApiError
   */
  public static listReportsByTypeApiV1ReportingTypeReportTypeGet(
    reportType: string
  ): CancelablePromise<ReportListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/reporting/type/{report_type}',
      path: {
        report_type: reportType,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Reports By Status
   * @param reportStatus
   * @returns ReportListResponse Successful Response
   * @throws ApiError
   */
  public static listReportsByStatusApiV1ReportingStatusReportStatusGet(
    reportStatus: string
  ): CancelablePromise<ReportListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/reporting/status/{report_status}',
      path: {
        report_status: reportStatus,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Download Report
   * @param reportId
   * @returns any Successful Response
   * @throws ApiError
   */
  public static downloadReportApiV1ReportingReportIdDownloadGet(
    reportId: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/reporting/{report_id}/download',
      path: {
        report_id: reportId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
