/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_api_v1_auth_login_post } from '../models/Body_login_api_v1_auth_login_post'
import type { RefreshTokenRequest } from '../models/RefreshTokenRequest'
import type { TokenResponse } from '../models/TokenResponse'
import type { UserResponse } from '../models/UserResponse'
import type { CancelablePromise } from '../core/CancelablePromise'
import { OpenAPI } from '../core/OpenAPI'
import { request as __request } from '../core/request'
export class AuthService {
  /**
   * Login
   * OAuth2 compatible token login.
   *
   * Use email as username in the OAuth2 password flow.
   * Returns both access token and refresh token.
   * @param formData
   * @returns TokenResponse Successful Response
   * @throws ApiError
   */
  public static loginApiV1AuthLoginPost(
    formData: Body_login_api_v1_auth_login_post
  ): CancelablePromise<TokenResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/auth/login',
      formData: formData,
      mediaType: 'application/x-www-form-urlencoded',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Refresh Access Token
   * Refresh access token using a valid refresh token.
   *
   * The refresh token must be valid and not expired.
   * Returns a new access token and refresh token.
   * @param requestBody
   * @returns TokenResponse Successful Response
   * @throws ApiError
   */
  public static refreshAccessTokenApiV1AuthRefreshPost(
    requestBody: RefreshTokenRequest
  ): CancelablePromise<TokenResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/auth/refresh',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Logout
   * Logout the current user by revoking their refresh token.
   * @returns void
   * @throws ApiError
   */
  public static logoutApiV1AuthLogoutPost(): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/auth/logout',
    })
  }
  /**
   * Get Current User Info
   * Get current authenticated user information.
   * @returns UserResponse Successful Response
   * @throws ApiError
   */
  public static getCurrentUserInfoApiV1AuthMeGet(): CancelablePromise<UserResponse> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/auth/me',
    })
  }
}
