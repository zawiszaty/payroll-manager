/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelContractRequest } from '../models/CancelContractRequest'
import type { ContractDetailView } from '../models/ContractDetailView'
import type { ContractListResponse } from '../models/ContractListResponse'
import type { CreateContractRequest } from '../models/CreateContractRequest'
import type { PaginatedResponse_ContractListView_ } from '../models/PaginatedResponse_ContractListView_'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class ContractsService {
  /**
   * Create Contract
   * @param requestBody
   * @returns ContractDetailView Successful Response
   * @throws ApiError
   */
  public static createContractApiV1ContractsPost(
    requestBody: CreateContractRequest
  ): CancelablePromise<ContractDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/contracts/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * List Contracts
   * @param page
   * @param limit
   * @returns PaginatedResponse_ContractListView_ Successful Response
   * @throws ApiError
   */
  public static listContractsApiV1ContractsGet(
    page: number = 1,
    limit: number = 100
  ): CancelablePromise<PaginatedResponse_ContractListView_> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/contracts/',
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
   * Get Contract
   * @param contractId
   * @returns ContractDetailView Successful Response
   * @throws ApiError
   */
  public static getContractApiV1ContractsContractIdGet(
    contractId: string
  ): CancelablePromise<ContractDetailView> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/contracts/{contract_id}',
      path: {
        contract_id: contractId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Contracts By Employee
   * @param employeeId
   * @returns ContractListResponse Successful Response
   * @throws ApiError
   */
  public static getContractsByEmployeeApiV1ContractsEmployeeEmployeeIdGet(
    employeeId: string
  ): CancelablePromise<ContractListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/contracts/employee/{employee_id}',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Get Active Contracts
   * @param employeeId
   * @returns ContractListResponse Successful Response
   * @throws ApiError
   */
  public static getActiveContractsApiV1ContractsEmployeeEmployeeIdActiveGet(
    employeeId: string
  ): CancelablePromise<ContractListResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/contracts/employee/{employee_id}/active',
      path: {
        employee_id: employeeId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Activate Contract
   * @param contractId
   * @returns ContractDetailView Successful Response
   * @throws ApiError
   */
  public static activateContractApiV1ContractsContractIdActivatePost(
    contractId: string
  ): CancelablePromise<ContractDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/contracts/{contract_id}/activate',
      path: {
        contract_id: contractId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Cancel Contract
   * @param contractId
   * @param requestBody
   * @returns ContractDetailView Successful Response
   * @throws ApiError
   */
  public static cancelContractApiV1ContractsContractIdCancelPost(
    contractId: string,
    requestBody: CancelContractRequest
  ): CancelablePromise<ContractDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/contracts/{contract_id}/cancel',
      path: {
        contract_id: contractId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Expire Contract
   * @param contractId
   * @returns ContractDetailView Successful Response
   * @throws ApiError
   */
  public static expireContractApiV1ContractsContractIdExpirePost(
    contractId: string
  ): CancelablePromise<ContractDetailView> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/contracts/{contract_id}/expire',
      path: {
        contract_id: contractId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
