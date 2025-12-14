/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * HAL-style pagination links
 */
export type PaginationLinks = {
  /**
   * Current page URL
   */
  self: string
  /**
   * First page URL
   */
  first: string
  /**
   * Last page URL
   */
  last: string
  /**
   * Next page URL (if available)
   */
  next?: string | null
  /**
   * Previous page URL (if available)
   */
  prev?: string | null
}
