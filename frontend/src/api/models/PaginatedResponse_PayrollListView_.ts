/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
import type { PayrollListView } from './PayrollListView'
export type PaginatedResponse_PayrollListView_ = {
  /**
   * List of items for the current page
   */
  items: Array<PayrollListView>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
