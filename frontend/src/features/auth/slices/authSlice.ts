import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { AuthState } from '../types'
import type { TokenResponse, UserResponse } from '@/api/models'
import { TOKEN_STORAGE_KEY, REFRESH_TOKEN_STORAGE_KEY } from '@/lib/constants'

const USER_STORAGE_KEY = 'user'

// Helper to safely parse stored user
const getStoredUser = (): UserResponse | null => {
  try {
    const stored = localStorage.getItem(USER_STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

const initialState: AuthState = {
  user: getStoredUser(),
  accessToken: localStorage.getItem(TOKEN_STORAGE_KEY),
  refreshToken: localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY),
  isAuthenticated: !!localStorage.getItem(TOKEN_STORAGE_KEY),
  isLoading: false,
  error: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.isLoading = true
      state.error = null
    },
    loginSuccess: (state, action: PayloadAction<TokenResponse>) => {
      const { access_token, refresh_token, user } = action.payload
      state.user = user
      state.accessToken = access_token
      state.refreshToken = refresh_token
      state.isAuthenticated = true
      state.isLoading = false
      state.error = null

      // Persist tokens and user to localStorage
      localStorage.setItem(TOKEN_STORAGE_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refresh_token)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.isLoading = false
      state.error = action.payload

      // Clear tokens and user from localStorage
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
      localStorage.removeItem(USER_STORAGE_KEY)
    },
    logout: (state) => {
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      state.isAuthenticated = false
      state.isLoading = false
      state.error = null

      // Clear tokens and user from localStorage
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
      localStorage.removeItem(USER_STORAGE_KEY)
    },
    refreshTokenSuccess: (state, action: PayloadAction<TokenResponse>) => {
      const { access_token, refresh_token, user } = action.payload
      state.user = user
      state.accessToken = access_token
      state.refreshToken = refresh_token
      state.isAuthenticated = true

      // Update tokens and user in localStorage
      localStorage.setItem(TOKEN_STORAGE_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refresh_token)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
    },
    updateUser: (state, action: PayloadAction<UserResponse>) => {
      state.user = action.payload
      // Persist updated user to localStorage
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(action.payload))
    },
    clearError: (state) => {
      state.error = null
    },
  },
})

export const {
  loginStart,
  loginSuccess,
  loginFailure,
  logout,
  refreshTokenSuccess,
  updateUser,
  clearError,
} = authSlice.actions

export default authSlice.reducer
