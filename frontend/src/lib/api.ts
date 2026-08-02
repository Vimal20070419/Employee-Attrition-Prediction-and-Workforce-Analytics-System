/**
 * AttritionIQ — Axios API Client
 * Centralized HTTP client with interceptors for JWT and error handling.
 */

import axios, { AxiosError, AxiosResponse } from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ========================
// Request Interceptor — Attach JWT
// ========================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('attritioniq_auth')
    if (token) {
      try {
        const parsed = JSON.parse(token)
        const accessToken = parsed?.state?.accessToken
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`
        }
      } catch {}
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ========================
// Response Interceptor — Token Refresh + Error Handling
// ========================
let isRefreshing = false
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: unknown) => void }> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error)
    else prom.resolve(token!)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as typeof error.config & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest!.headers!.Authorization = `Bearer ${token}`
          return api(originalRequest!)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const stored = localStorage.getItem('attritioniq_auth')
        const parsed = stored ? JSON.parse(stored) : null
        const refreshToken = parsed?.state?.refreshToken

        if (!refreshToken) throw new Error('No refresh token')

        const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
        const newToken = response.data.access_token

        // Update stored token
        if (parsed) {
          parsed.state.accessToken = newToken
          localStorage.setItem('attritioniq_auth', JSON.stringify(parsed))
        }

        processQueue(null, newToken)
        originalRequest!.headers!.Authorization = `Bearer ${newToken}`
        return api(originalRequest!)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('attritioniq_auth')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// ========================
// API Helper Functions
// ========================
export const apiGet = <T>(url: string, params?: object) =>
  api.get<T>(url, { params }).then((r) => r.data)

export const apiPost = <T>(url: string, data?: object) =>
  api.post<T>(url, data).then((r) => r.data)

export const apiPatch = <T>(url: string, data?: object) =>
  api.patch<T>(url, data).then((r) => r.data)

export const apiDelete = (url: string) =>
  api.delete(url).then((r) => r.data)
