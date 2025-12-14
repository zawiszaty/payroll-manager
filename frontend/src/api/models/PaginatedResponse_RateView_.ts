/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
import type { RateView } from './RateView'
export type PaginatedResponse_RateView_ = {
  /**
   * List of items for the current page
   */
  items: Array<RateView>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
