/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApproveTimesheetRequest } from '../models/ApproveTimesheetRequest'
import type { CreateTimesheetRequest } from '../models/CreateTimesheetRequest'
import type { HoursSummaryResponse } from '../models/HoursSummaryResponse'
import type { RejectTimesheetRequest } from '../models/RejectTimesheetRequest'
import type { TimesheetResponse } from '../models/TimesheetResponse'
import type { UpdateTimesheetRequest } from '../models/UpdateTimesheetRequest'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class TimesheetsService {
  /**
   * List Timesheets
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static listTimesheetsApiV1TimesheetsGet(): CancelablePromise<Array<TimesheetResponse>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/',
    })
  }
  /**
   * Create Timesheet
   * @param requestBody
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static createTimesheetApiV1TimesheetsPost(
    requestBody: CreateTimesheetRequest
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/timesheets/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Timesheet
   * @param timesheetId
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static getTimesheetApiV1TimesheetsTimesheetIdGet(
    timesheetId: string
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/{timesheet_id}',
      path: {
        timesheet_id: timesheetId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Update Timesheet
   * @param timesheetId
   * @param requestBody
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static updateTimesheetApiV1TimesheetsTimesheetIdPut(
    timesheetId: string,
    requestBody: UpdateTimesheetRequest
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'PUT',
      url: '/api/v1/timesheets/{timesheet_id}',
      path: {
        timesheet_id: timesheetId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Delete Timesheet
   * @param timesheetId
   * @returns void
   * @throws ApiError
   */
  public static deleteTimesheetApiV1TimesheetsTimesheetIdDelete(
    timesheetId: string
  ): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/api/v1/timesheets/{timesheet_id}',
      path: {
        timesheet_id: timesheetId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Timesheets By Employee
   * @param employeeId
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static getTimesheetsByEmployeeApiV1TimesheetsEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<Array<TimesheetResponse>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Timesheets By Employee And Date Range
   * @param employeeId
   * @param startDate
   * @param endDate
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static getTimesheetsByEmployeeAndDateRangeApiV1TimesheetsEmployeeEmployeeIdPeriodGet(
    employeeId: string,
    startDate: string,
    endDate: string
  ): CancelablePromise<Array<TimesheetResponse>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/employee/{employee_id}/period',
      path: {
        employee_id: employeeId,
      },
      query: {
        start_date: startDate,
        end_date: endDate,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Timesheets By Status
   * @param statusValue
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static getTimesheetsByStatusApiV1TimesheetsStatusStatusValueGet(
    statusValue: string
  ): CancelablePromise<Array<TimesheetResponse>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/status/{status_value}',
      path: {
        status_value: statusValue,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Pending Approval
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static getPendingApprovalApiV1TimesheetsPendingApprovalListGet(): CancelablePromise<
    Array<TimesheetResponse>
  > {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/pending-approval/list',
    })
  }
  /**
   * Sum Hours In Interval
   * @param employeeId
   * @param startDate
   * @param endDate
   * @returns HoursSummaryResponse Successful Response
   * @throws ApiError
   */
  public static sumHoursInIntervalApiV1TimesheetsEmployeeEmployeeIdHoursSummaryGet(
    employeeId: string,
    startDate: string,
    endDate: string
  ): CancelablePromise<HoursSummaryResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/timesheets/employee/{employee_id}/hours-summary',
      path: {
        employee_id: employeeId,
      },
      query: {
        start_date: startDate,
        end_date: endDate,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Submit Timesheet
   * @param timesheetId
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static submitTimesheetApiV1TimesheetsTimesheetIdSubmitPost(
    timesheetId: string
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/timesheets/{timesheet_id}/submit',
      path: {
        timesheet_id: timesheetId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Approve Timesheet
   * @param timesheetId
   * @param requestBody
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static approveTimesheetApiV1TimesheetsTimesheetIdApprovePost(
    timesheetId: string,
    requestBody: ApproveTimesheetRequest
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/timesheets/{timesheet_id}/approve',
      path: {
        timesheet_id: timesheetId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Reject Timesheet
   * @param timesheetId
   * @param requestBody
   * @returns TimesheetResponse Successful Response
   * @throws ApiError
   */
  public static rejectTimesheetApiV1TimesheetsTimesheetIdRejectPost(
    timesheetId: string,
    requestBody: RejectTimesheetRequest
  ): CancelablePromise<TimesheetResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/timesheets/{timesheet_id}/reject',
      path: {
        timesheet_id: timesheetId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
