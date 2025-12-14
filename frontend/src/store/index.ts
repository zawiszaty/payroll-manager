import { configureStore } from '@reduxjs/toolkit'
import authReducer from '@/features/auth/slices/authSlice'

/**
 * Redux store configuration
 * Slices will be added as we implement features
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    // ui: uiReducer,
    // notifications: notificationsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for serializability checks
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: import.meta.env.DEV,
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
