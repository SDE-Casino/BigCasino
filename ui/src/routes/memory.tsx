import { createFileRoute, redirect, Outlet, useLocation, useNavigate } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Clock, Gamepad2, Trophy, Play } from 'lucide-react'
import { useState } from 'react'

const MEMORY_SERVICE_URL = 'http://localhost:8003'

interface GameSize {
  label: string
  size: number
  description: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
}

const GAME_SIZES: GameSize[] = [
  { label: '4x4', size: 8, description: 'Perfect for beginners', difficulty: 'Easy' },
  { label: '6x6', size: 18, description: 'A balanced challenge', difficulty: 'Medium' },
  { label: '8x8', size: 32, description: 'For memory masters', difficulty: 'Hard' },
]

export const Route = createFileRoute('/memory')({
  component: Memory,
})

function Memory() {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [showSizePopup, setShowSizePopup] = useState(false)

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  const isGameRoute = location.pathname.startsWith('/memory/game/')

  const handleNewGame = () => {
    setShowSizePopup(true)
  }

  const handleSizeSelect = async (size: number) => {
    setShowSizePopup(false)
    try {
      const response = await fetch(`${MEMORY_SERVICE_URL}/create_game`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: user?.id || 1, size }),
      })
      if (!response.ok) throw new Error('Failed to create game')
      const data = await response.json()
      navigate({ to: '/memory/game/$id', params: { id: data.game.id.toString() } })
    } catch (err) {
      console.error('Failed to create game:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto p-6">
        {!isGameRoute && (
          <>
            {/* Header */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-slate-800 mb-3">Memory Game</h1>
              <p className="text-slate-600 max-w-xl mx-auto">
                Test your memory by matching pairs of cards. Flip two cards at a time and find all matching pairs to win.
              </p>
            </div>

            {/* Quick Start */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-8">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <Play size={24} className="text-blue-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">Ready to play?</h2>
                    <p className="text-slate-500 text-sm">Start a new game</p>
                  </div>
                </div>
                <button
                  onClick={handleNewGame}
                  className="flex items-center gap-2 bg-blue-600 text-white font-medium py-2.5 px-5 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus size={18} />
                  New Game
                </button>
              </div>
            </div>

            {/* How to Play */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-8">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <Gamepad2 size={20} className="text-blue-500" />
                How to Play
              </h2>
              <div className="grid md:grid-cols-3 gap-5">
                <div className="text-center">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-semibold">1</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Flip Cards</h3>
                  <p className="text-slate-500 text-sm">Click to reveal card images</p>
                </div>
                <div className="text-center">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-semibold">2</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Match Pairs</h3>
                  <p className="text-slate-500 text-sm">Find matching card pairs</p>
                </div>
                <div className="text-center">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-semibold">3</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Collect & Win</h3>
                  <p className="text-slate-500 text-sm">Collect more pairs than opponent</p>
                </div>
              </div>
            </div>

            {/* Previous Games */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <Trophy size={20} className="text-amber-500" />
                Previous Games
              </h2>
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock size={32} className="text-slate-400" />
                </div>
                <h3 className="text-lg font-medium text-slate-900 mb-1">No games played yet</h3>
                <p className="text-slate-500 text-sm mb-4">Start your first game</p>
                <button
                  onClick={handleNewGame}
                  className="inline-flex items-center gap-2 text-slate-600 hover:text-blue-600 font-medium py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  <Plus size={16} />
                  Start Game
                </button>
              </div>
            </div>
          </>
        )}

        <Outlet />

        {/* Size Selection Popup */}
        {showSizePopup && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-semibold text-slate-900 mb-2">Select Game Size</h2>
              <p className="text-slate-500 text-sm mb-5">Choose your difficulty level</p>
              <div className="space-y-3 mb-5">
                {GAME_SIZES.map((gameSize) => (
                  <button
                    key={gameSize.label}
                    onClick={() => handleSizeSelect(gameSize.size)}
                    className="w-full flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50 transition-colors text-left group"
                  >
                    <div>
                      <span className="font-semibold text-slate-900 group-hover:text-blue-600">{gameSize.label}</span>
                      <span className="text-slate-400 mx-2">•</span>
                      <span className="text-slate-500 text-sm">{gameSize.difficulty}</span>
                      <p className="text-slate-400 text-xs mt-1">{gameSize.description}</p>
                    </div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowSizePopup(false)}
                className="w-full bg-slate-100 text-slate-700 font-medium py-2.5 px-4 rounded-lg hover:bg-slate-200 transition-colors"
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
