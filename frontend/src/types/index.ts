export interface HealthResponse {
  status: string
  database: string
}

export interface User {
  id: number
  name: string
  email: string
  is_active: boolean
  created_at?: string | null
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}
