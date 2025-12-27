import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { ReactNode } from 'react'
import { authService } from '../services/auth'
import type { UserCredentials } from '../types/auth'

interface User {
  id: string  // Changed to UUID string
  username: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: UserCredentials) => Promise<void>
  register: (credentials: UserCredentials) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Helper function to parse JWT and get expiration time
function getTokenExpiration(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = () => {
      const storedUser = authService.getUser()
      const token = authService.getAccessToken()

      if (storedUser && token) {
        setUser(storedUser)
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  // Set up automatic token refresh
  useEffect(() => {
    if (!user || isLoading) return

    const token = authService.getAccessToken()
    if (!token) return

    const expiration = getTokenExpiration(token)
    if (!expiration) return

    // Refresh token 5 minutes before it expires
    const refreshTime = expiration - Date.now() - 5 * 60 * 1000

    if (refreshTime <= 0) {
      // Token is already expired or will expire soon, refresh immediately
      refresh()
      return
    }

    const timeoutId = setTimeout(() => {
      refresh()
    }, refreshTime)

    return () => clearTimeout(timeoutId)
  }, [user, isLoading])

  const login = useCallback(async (credentials: UserCredentials) => {
    try {
      const response = await authService.login(credentials)
      setUser({ id: response.id, username: response.username })
    } catch (error) {
      setUser(null)
      throw error
    }
  }, [])

  const register = useCallback(async (credentials: UserCredentials) => {
    try {
      const response = await authService.register(credentials)
      setUser({ id: response.id, username: response.username })
    } catch (error) {
      setUser(null)
      throw error
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
    }
  }, [])

  const refresh = useCallback(async () => {
    try {
      await authService.refresh()
      const storedUser = authService.getUser()
      if (storedUser) {
        setUser(storedUser)
      }
    } catch (error) {
      console.error('Token refresh error:', error)
      setUser(null)
      throw error
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        register,
        logout,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
