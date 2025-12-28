export enum AuthProvider {
  LOCAL = 'local',
  GOOGLE = 'google'
}

export interface User {
  id: string  // Changed to UUID string
  username: string
  provider?: AuthProvider
}

export interface UserCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  id: string  // Changed to UUID string
  username: string
  access_token: string
}

export interface GoogleAuthResponse {
  id: string
  username: string
  access_token: string
}

export interface RefreshResponse {
  access_token: string
}

export interface LogoutResponse {
  detail: string
}

export interface AuthError {
  detail: string
}
