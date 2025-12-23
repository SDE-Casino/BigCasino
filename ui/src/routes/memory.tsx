import { createFileRoute, redirect, Link, Outlet, useLocation, useNavigate } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Clock } from 'lucide-react'
import { useState } from 'react'

interface GameSize {
  label: string
  size: number
}

const GAME_SIZES: GameSize[] = [
  { label: '4x4', size: 8 },
  { label: '6x6', size: 18 },
  { label: '8x8', size: 32 },
]

export const Route = createFileRoute('/memory')({
  component: Memory,
})

function Memory() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [showSizePopup, setShowSizePopup] = useState(false)

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  const isGameRoute = location.pathname === '/memory/game'

  const handleNewGame = () => {
    setShowSizePopup(true)
  }

  const handleSizeSelect = (size: number) => {
    setShowSizePopup(false)
    navigate({ to: '/memory/game', search: { size } })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 to-teal-100 p-4">
      <div className="max-w-4xl mx-auto">
        {!isGameRoute && (
          <>
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800">Memory Games</h1>
              <button
                onClick={handleNewGame}
                className="flex items-center gap-2 bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-2 px-4 rounded-lg hover:from-green-600 hover:to-teal-700 transition-all duration-300"
              >
                <Plus size={20} />
                New Game
              </button>
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

        {showSizePopup && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Select Game Size</h2>
              <div className="grid grid-cols-2 gap-4">
                {GAME_SIZES.map((gameSize) => (
                  <button
                    key={gameSize.label}
                    onClick={() => handleSizeSelect(gameSize.size)}
                    className="bg-gradient-to-r from-green-500 to-teal-600 text-white font-bold py-4 px-6 rounded-xl hover:from-green-600 hover:to-teal-700 transition-all duration-300 text-xl"
                  >
                    {gameSize.label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowSizePopup(false)}
                className="w-full mt-4 bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-all duration-300"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}