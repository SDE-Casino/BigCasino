import type {
    UserCredentials,
    AuthResponse,
    RefreshResponse,
    LogoutResponse,
    AuthError,
} from '../types/auth'

const API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8009'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

// Helper function to parse JWT and get user ID from token
function getUserIdFromToken(token: string): string | null {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.sub || null
    } catch {
        return null
    }
}

class AuthService {
    private getHeaders(): HeadersInit {
        const token = this.getAccessToken()
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        }
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }
        return headers
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        if (!response.ok) {
            const error: AuthError = await response.json()
            throw new Error(error.detail || 'An error occurred')
        }
        return response.json()
    }

    setAccessToken(token: string): void {
        localStorage.setItem(ACCESS_TOKEN_KEY, token)
    }

    getAccessToken(): string | null {
        return localStorage.getItem(ACCESS_TOKEN_KEY)
    }

    setRefreshToken(token: string): void {
        localStorage.setItem(REFRESH_TOKEN_KEY, token)
    }

    getRefreshToken(): string | null {
        return localStorage.getItem(REFRESH_TOKEN_KEY)
    }

    setUser(user: { id: string; username: string }): void {
        localStorage.setItem(USER_KEY, JSON.stringify(user))
    }

    getUser(): { id: string; username: string } | null {
        const userStr = localStorage.getItem(USER_KEY)
        if (userStr) {
            try {
                return JSON.parse(userStr)
            } catch {
                return null
            }
        }
        return null
    }

    clearAuthData(): void {
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
    }

    async login(credentials: UserCredentials): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: this.getHeaders(),
            credentials: 'include',
            body: JSON.stringify(credentials),
        })

        const data = await this.handleResponse<AuthResponse>(response)

        // Store access token and user data
        this.setAccessToken(data.access_token)
        // Extract user ID from JWT token
        const userId = getUserIdFromToken(data.access_token) || data.id
        this.setUser({ id: userId, username: data.username })

        return data
    }

    async register(credentials: UserCredentials): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: this.getHeaders(),
            credentials: 'include',
            body: JSON.stringify(credentials),
        })

        const data = await this.handleResponse<AuthResponse>(response)

        // Store access token and user data
        this.setAccessToken(data.access_token)
        // Extract user ID from JWT token
        const userId = getUserIdFromToken(data.access_token) || data.id
        this.setUser({ id: userId, username: data.username })

        return data
    }

    async refresh(): Promise<RefreshResponse> {
        const refreshToken = this.getRefreshToken()
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        }

        // Send refresh token via header since cross-origin cookies are problematic
        if (refreshToken) {
            headers['Authorization'] = `Refresh ${refreshToken}`
        }

        const response = await fetch(`${API_URL}/refresh`, {
            method: 'POST',
            headers,
            credentials: 'include',
        })

        const data = await this.handleResponse<RefreshResponse>(response)

        // Update access token
        this.setAccessToken(data.access_token)
        // Refresh user ID from new token
        const userId = getUserIdFromToken(data.access_token)
        if (userId) {
            const existingUser = this.getUser()
            if (existingUser) {
                this.setUser({ id: userId, username: existingUser.username })
            }
        }

        return data
    }

    async logout(): Promise<LogoutResponse> {
        const response = await fetch(`${API_URL}/logout`, {
            method: 'POST',
            headers: this.getHeaders(),
            credentials: 'include',
        })

        const data = await this.handleResponse<LogoutResponse>(response)

        // Clear local auth data
        this.clearAuthData()

        return data
    }

    initiateGoogleLogin(): void {
        // Redirect to process-centric Google login endpoint
        window.location.href = `${API_URL}/google/login`
    }

    async handleGoogleCallback(): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/google/verify_token`, {
            method: 'GET',
            credentials: 'include',
            headers: this.getHeaders(),
        })

        const data = await this.handleResponse<AuthResponse>(response)

        if (data.access_token) {
            this.setAccessToken(data.access_token)
            const userId = getUserIdFromToken(data.access_token) || data.id
            this.setUser({ id: userId, username: data.username })
        }

        return data
    }

    // Handle tokens passed via URL hash after Google OAuth redirect
    handleGoogleCallbackFromHash(): { success: boolean; username?: string } {
        const hash = window.location.hash.substring(1) // Remove the # character
        if (!hash) {
            return { success: false }
        }

        const params = new URLSearchParams(hash)
        const accessToken = params.get('access_token')
        const refreshToken = params.get('refresh_token')

        if (accessToken && refreshToken) {
            this.setAccessToken(accessToken)
            this.setRefreshToken(refreshToken)

            // Extract user info from token
            const userId = getUserIdFromToken(accessToken)
            if (userId) {
                // Try to get email from the token payload
                try {
                    const payload = JSON.parse(atob(accessToken.split('.')[1]))
                    const username = payload.email || payload.username || 'Google User'
                    this.setUser({ id: userId, username })

                    // Clear the hash from URL for cleaner look
                    window.history.replaceState(null, '', window.location.pathname)

                    return { success: true, username }
                } catch {
                    return { success: false }
                }
            }
        }

        return { success: false }
    }

    isAuthenticated(): boolean {
        return this.getAccessToken() !== null && this.getUser() !== null
    }
}

export const authService = new AuthService()
