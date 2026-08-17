import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import * as authApi from '../api/auth'
import {
  clearStoredTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
  storeTokens,
} from '../api/client'
import type { LoginRequest, RegisterRequest, User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (payload: LoginRequest) => Promise<void>
  register: (payload: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Rehydrate the session if we have a stored access token.
    const bootstrap = async () => {
      if (!getStoredAccessToken()) {
        setLoading(false)
        return
      }
      try {
        const me = await authApi.getMe()
        setUser(me)
      } catch {
        clearStoredTokens()
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    bootstrap()
  }, [])

  const login = async (payload: LoginRequest) => {
    const tokens = await authApi.login(payload)
    storeTokens(tokens)
    setUser(tokens.user)
  }

  const register = async (payload: RegisterRequest) => {
    const tokens = await authApi.register(payload)
    storeTokens(tokens)
    setUser(tokens.user)
  }

  const logout = async () => {
    const refreshToken = getStoredRefreshToken()
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } finally {
      clearStoredTokens()
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: !!user, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
