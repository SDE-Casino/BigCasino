import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'

interface User {
    id: number
}

interface AuthContextType {
    user: User | null
    isAuthenticated: boolean
    login: () => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>({ id: 1 })

    const login = () => {
        setUser({ id: 1 })
    }

    const logout = () => {
        setUser(null)
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: user !== null,
                login,
                logout,
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