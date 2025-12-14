/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmployeeListView } from './EmployeeListView'
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
export type PaginatedResponse_EmployeeListView_ = {
  /**
   * List of items for the current page
   */
  items: Array<EmployeeListView>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
