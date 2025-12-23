import { createFileRoute, redirect } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/solitaire')({
  component: Solitaire,
})

function Solitaire() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-red-100 to-orange-100 p-4">
      <div className="w-full max-w-md p-8 rounded-xl backdrop-blur-md bg-white/50 shadow-xl border border-white/20">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
          Solitaire
        </h1>
        <p className="text-center text-gray-600">
          Solitaire route placeholder
        </p>
      </div>
    </div>
  )
}