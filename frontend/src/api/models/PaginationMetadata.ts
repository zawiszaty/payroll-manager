/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Pagination metadata
 */
export type PaginationMetadata = {
  /**
   * Total number of items in the database
   */
  total_items: number
  /**
   * Total number of pages
   */
  total_pages: number
  /**
   * Current page number (1-indexed)
   */
  current_page: number
  /**
   * Number of items per page
   */
  page_size: number
  /**
   * Whether there is a next page
   */
  has_next: boolean
  /**
   * Whether there is a previous page
   */
  has_previous: boolean
}
