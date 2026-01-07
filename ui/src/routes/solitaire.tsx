import { createFileRoute, redirect, Outlet, useLocation, useNavigate } from '@tanstack/react-router'
import { Plus, Play, Gamepad2, RotateCcw, Trophy } from 'lucide-react'
import { useState, useEffect } from 'react'
import { authService } from '../services/auth'

const SOLITAIRE_SERVICE_URL = 'http://localhost:8010'

// Store game states in window object for access across routes
// @ts-ignore
if (!(window as any).__solitaireGameStates) {
  ; (window as any).__solitaireGameStates = {}
}

interface LeaderboardEntry {
  user_id: string
  played_games: number
  games_won: number
}

export const Route = createFileRoute('/solitaire')({
  beforeLoad: async ({ location }) => {
    // Check if user has a token in localStorage
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw redirect({
        to: '/auth',
        search: {
          redirect: location.href
        }
      })
    }
  },
  component: Solitaire,
})

function Solitaire() {
  const location = useLocation()
  const navigate = useNavigate()
  const [isCreatingGame, setIsCreatingGame] = useState(false)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [isLoadingLeaderboard, setIsLoadingLeaderboard] = useState(false)

  const isGameRoute = location.pathname.startsWith('/solitaire/game/')

  useEffect(() => {
    if (!isGameRoute) {
      fetchLeaderboard()
    }
  }, [isGameRoute])

  const fetchLeaderboard = async () => {
    setIsLoadingLeaderboard(true)
    try {
      const token = authService.getAccessToken()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/leaderboard`, {
        headers
      })

      if (response.ok) {
        const data = await response.json()
        setLeaderboard(data)
      }
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error)
    } finally {
      setIsLoadingLeaderboard(false)
    }
  }

  const handleNewGame = async () => {
    setIsCreatingGame(true)
    try {
      const token = authService.getAccessToken()
      console.log('Creating game with token:', token ? 'Token exists' : 'No token found')

      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/create_game`, {
        method: 'POST',
        headers,
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json()
        console.error('Error response:', errorData)
        throw new Error(errorData.detail || 'Failed to create game')
      }

      const data = await response.json()
      console.log('Game created:', data)

        // Store game state in window object for later use
        ; (window as any).__solitaireGameStates[data.game_id] = data.game_state
      navigate({ to: '/solitaire/game/$id', params: { id: data.game_id } })
    } catch (err) {
      console.error('Failed to create game:', err)
      setIsCreatingGame(false)
    }
  }

  // Clean up loading state when navigating to game route
  useEffect(() => {
    if (isGameRoute) {
      setIsCreatingGame(false)
    }
  }, [isGameRoute])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto p-6">
        {!isGameRoute && (
          <>
            {/* Header */}
            <div className="text-center mb-12 animate-in fade-in slide-in-from-top-4 duration-500">
              <h1 className="text-4xl font-bold text-slate-800 mb-3">Solitaire</h1>
              <p className="text-slate-600 max-w-xl mx-auto">
                Classic Klondike Solitaire. Move all cards to foundation piles, building up from Ace to King by suit.
              </p>
            </div>

            {/* Quick Start */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100 hover:shadow-md transition-shadow duration-300">
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
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200 hover:shadow-md transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <Gamepad2 size={20} className="text-blue-500" />
                How to Play
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 text-xs font-semibold">1</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 mb-1">Build Foundation Piles</h3>
                    <p className="text-slate-500 text-sm">Move all cards to four foundation piles, building up from Ace to King by suit (♥, ♦, ♣, ♠).</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 text-xs font-semibold">2</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 mb-1">Organize Tableau</h3>
                    <p className="text-slate-500 text-sm">Build down in tableau columns, alternating colors (red on black, black on red).</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 text-xs font-semibold">3</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 mb-1">Use Stock and Talon</h3>
                    <p className="text-slate-500 text-sm">Draw cards from stock pile to talon when you need more cards. Move cards from talon to tableau or foundation.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 text-xs font-semibold">4</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 mb-1">Move Cards</h3>
                    <p className="text-slate-500 text-sm">Click on a card to select it, then click on a valid destination. Only Kings can be placed in empty tableau columns.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Game Tips */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-300 hover:shadow-md transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <RotateCcw size={20} className="text-blue-500" />
                Tips & Strategy
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                  <h3 className="font-medium text-slate-900 mb-2">Reveal Face-Down Cards</h3>
                  <p className="text-slate-500 text-sm">Prioritize moves that reveal face-down cards in tableau.</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                  <h3 className="font-medium text-slate-900 mb-2">Empty Columns</h3>
                  <p className="text-slate-500 text-sm">Use empty columns strategically - only Kings can fill them.</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                  <h3 className="font-medium text-slate-900 mb-2">Build Foundations</h3>
                  <p className="text-slate-500 text-sm">Move Aces to foundation early and build them up when possible.</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                  <h3 className="font-medium text-slate-900 mb-2">Plan Ahead</h3>
                  <p className="text-slate-500 text-sm">Look for moves that create opportunities for future plays.</p>
                </div>
              </div>
            </div>

            {/* Leaderboard */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-400 hover:shadow-md transition-shadow duration-300 mb-8">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <Trophy size={20} className="text-yellow-500" />
                Leaderboard
              </h2>

              {isLoadingLeaderboard ? (
                <div className="flex justify-center py-8">
                  <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                </div>
              ) : leaderboard.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 font-medium">
                      <tr>
                        <th className="px-4 py-3 rounded-l-lg">User</th>
                        <th className="px-4 py-3">Games Played</th>
                        <th className="px-4 py-3">Games Won</th>
                        <th className="px-4 py-3 rounded-r-lg">Win Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {leaderboard
                        .sort((a, b) => b.games_won - a.games_won)
                        .slice(0, 10)
                        .map((entry) => {
                          const winRate = entry.played_games > 0
                            ? Math.round((entry.games_won / entry.played_games) * 100)
                            : 0;
                          const isCurrentUser = authService.getUser()?.id === entry.user_id;

                          return (
                            <tr key={entry.user_id} className={`hover:bg-slate-50 transition-colors ${isCurrentUser ? 'bg-blue-50/50' : ''}`}>
                              <td className="px-4 py-3 font-medium text-slate-900">
                                {isCurrentUser ? `${entry.user_id} (You)` : entry.user_id}
                              </td>
                              <td className="px-4 py-3 text-slate-600">{entry.played_games}</td>
                              <td className="px-4 py-3 text-slate-600">{entry.games_won}</td>
                              <td className="px-4 py-3 text-slate-600">
                                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${winRate >= 50 ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                                  }`}>
                                  {winRate}%
                                </span>
                              </td>
                            </tr>
                          )
                        })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  No games played yet. Be the first to top the leaderboard!
                </div>
              )}
            </div>
          </>
        )}

        <Outlet />

        {/* Loading Overlay */}
        {isCreatingGame && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 animate-in fade-in duration-300">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-sm w-full text-center animate-in zoom-in-95 duration-300 hover:scale-105 transition-transform duration-300">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                <div className="absolute inset-0 rounded-full border-4 border-blue-300 border-t-transparent animate-spin"></div>
                <Play size={36} className="text-blue-600 animate-pulse" />
              </div>
              <h2 className="text-xl font-semibold text-slate-900 mb-2">Creating Game...</h2>
              <p className="text-slate-500 text-sm mb-4">Setting up your solitaire game</p>
              <div className="flex justify-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

