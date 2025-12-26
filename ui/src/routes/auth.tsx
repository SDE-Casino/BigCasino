import { createFileRoute, redirect } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/auth')({
    component: Auth,
})

function Auth() {
    const { isAuthenticated, login } = useAuth()

    if (isAuthenticated) {
        throw redirect({ to: '/' })
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 p-4">
            <div className="w-full max-w-md p-8 rounded-xl backdrop-blur-md bg-white/50 shadow-xl border border-white/20">
                <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
                    Welcome to Big Casino
                </h1>
                <p className="text-center text-gray-600 mb-8">
                    Please sign in to access the games
                </p>
                <button
                    type="button"
                    onClick={login}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                    Sign In
                </button>
            </div>
        </div>
    )
}
