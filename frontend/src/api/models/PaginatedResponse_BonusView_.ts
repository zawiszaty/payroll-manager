/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BonusView } from './BonusView'
import type { PaginationLinks } from './PaginationLinks'
import type { PaginationMetadata } from './PaginationMetadata'
export type PaginatedResponse_BonusView_ = {
  /**
   * List of items for the current page
   */
  items: Array<BonusView>
  metadata: PaginationMetadata
  /**
   * HAL-style navigation links
   */
  _links: PaginationLinks
}
