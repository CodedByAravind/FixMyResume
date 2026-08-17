import apiClient from './client'
import type { LoginRequest, RegisterRequest, TokenPair, User } from '../types'

export async function register(payload: RegisterRequest): Promise<TokenPair> {
  const resp = await apiClient.post<TokenPair>('/api/v1/auth/register', payload)
  return resp.data
}

export async function login(payload: LoginRequest): Promise<TokenPair> {
  const resp = await apiClient.post<TokenPair>('/api/v1/auth/login', payload)
  return resp.data
}

export async function logout(refreshToken: string): Promise<void> {
  await apiClient.post('/api/v1/auth/logout', { refresh_token: refreshToken })
}

export async function getMe(): Promise<User> {
  const resp = await apiClient.get<User>('/api/v1/auth/me')
  return resp.data
}
