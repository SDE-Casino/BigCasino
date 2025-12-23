import { createFileRoute, redirect, Link, Outlet, useLocation } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Clock } from 'lucide-react'

export const Route = createFileRoute('/memory')({
  component: Memory,
})

function Memory() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  const isGameRoute = location.pathname === '/memory/game'

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 to-teal-100 p-4">
      <div className="max-w-4xl mx-auto">
        {!isGameRoute && (
          <>
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800">Memory Games</h1>
              <Link
                to="/memory/game"
                className="flex items-center gap-2 bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-2 px-4 rounded-lg hover:from-green-600 hover:to-teal-700 transition-all duration-300"
              >
                <Plus size={20} />
                New Game
              </Link>
            </div>

            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Previous Games</h2>
              <div className="text-center py-12 text-gray-500">
                <Clock size={48} className="mx-auto mb-4 text-gray-400" />
                <p>No previous games found</p>
                <p className="text-sm mt-2">Start a new game to begin playing!</p>
              </div>
            </div>
          </>
        )}

        <Outlet />
      </div>
    </div>
  )
}