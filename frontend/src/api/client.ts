import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL, TOKEN_STORAGE_KEY, REFRESH_TOKEN_STORAGE_KEY } from '../lib/constants'

/**
 * Axios instance for API calls
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request interceptor - Add auth token to requests
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }

    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - Handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data)
    }
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Log errors
    console.error('[API Response Error]', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
    })

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)

        if (!refreshToken) {
          // No refresh token, redirect to login
          handleLogout()
          return Promise.reject(error)
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data

        // Update tokens
        localStorage.setItem(TOKEN_STORAGE_KEY, access_token)
        localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, newRefreshToken)

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }

        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        console.error('[Token Refresh Failed]', refreshError)
        handleLogout()
        return Promise.reject(refreshError)
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.warn('[Forbidden] You do not have permission to access this resource')
      // Optionally show a toast notification
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      console.warn('[Not Found] Resource not found')
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('[Server Error] Internal server error')
      // Optionally show a toast notification
    }

    return Promise.reject(error)
  }
)

/**
 * Handle logout - Clear tokens and redirect to login
 */
function handleLogout() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
  localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
  localStorage.removeItem('payroll_user')

  // Redirect to login page
  window.location.href = '/login'
}

export default apiClient
