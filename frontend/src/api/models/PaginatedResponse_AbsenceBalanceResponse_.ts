/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceBalanceResponse } from './AbsenceBalanceResponse'
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
export type PaginatedResponse_AbsenceBalanceResponse_ = {
  /**
   * List of items for the current page
   */
  items: Array<AbsenceBalanceResponse>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
