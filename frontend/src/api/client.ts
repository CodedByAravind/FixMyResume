import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { TokenPair } from '../types'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function storeTokens(tokens: Pick<TokenPair, 'access_token' | 'refresh_token'>): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token)
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
}

export function clearStoredTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach the access token to outgoing requests.
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getStoredAccessToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On a 401, attempt a single token refresh and retry the original request.
let refreshing: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  if (refreshing) {
    return refreshing
  }
  refreshing = (async () => {
    const refreshToken = getStoredRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }
    const resp = await axios.post<TokenPair>(
      `${apiClient.defaults.baseURL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken },
    )
    storeTokens(resp.data)
    return resp.data.access_token
  })().finally(() => {
    refreshing = null
  })
  return refreshing
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      try {
        const newToken = await refreshAccessToken()
        if (original.headers) {
          original.headers.Authorization = `Bearer ${newToken}`
        }
        return apiClient(original)
      } catch {
        clearStoredTokens()
        // Redirect to login if we're not already there.
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
