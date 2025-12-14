/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AbsenceResponse } from './AbsenceResponse'
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
export type PaginatedResponse_AbsenceResponse_ = {
  /**
   * List of items for the current page
   */
  items: Array<AbsenceResponse>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
