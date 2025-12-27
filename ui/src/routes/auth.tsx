import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { useState, useEffect } from 'react'
import type { UserCredentials } from '../types/auth'

export const Route = createFileRoute('/auth')({
  component: Auth,
})

function Auth() {
  const { isAuthenticated, login, register, isLoading } = useAuth()
  const navigate = useNavigate()
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Redirect if already authenticated (use effect to avoid render issues)
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate({ to: '/', replace: true })
    }
  }, [isLoading, isAuthenticated, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const credentials: UserCredentials = { username, password }

      if (isLoginMode) {
        await login(credentials)
      } else {
        await register(credentials)
      }

      // Redirect to home page after successful auth
      navigate({ to: '/' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 to-purple-100">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 p-4">
      <div className="w-full max-w-md p-8 rounded-xl backdrop-blur-md bg-white/50 shadow-xl border border-white/20">
        <h1 className="text-3xl font-bold mb-2 text-center text-gray-800">
          Welcome to Big Casino
        </h1>
        <p className="text-center text-gray-600 mb-8">
          {isLoginMode ? 'Sign in to access the games' : 'Create an account to get started'}
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Processing...' : isLoginMode ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLoginMode(!isLoginMode)
              setError('')
            }}
            className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            {isLoginMode
              ? "Don't have an account? Sign up"
              : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  )
}
