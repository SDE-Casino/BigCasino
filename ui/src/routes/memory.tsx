import { createFileRoute, redirect, Outlet, useLocation, useNavigate } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Clock, Gamepad2, Trophy, Play, User, ChevronRight, Trash2, AlertTriangle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { authService } from '../services/auth'

const MEMORY_SERVICE_URL = 'http://localhost:8003'

interface Card {
  id: number
  localId: number
  flipped: boolean
  image: string
  kindId: number
  ownedBy: boolean | null
}

interface Game {
  gameId: number
  size: number
  winner: string | null
  player1Cards: Card[]
  player2Cards: Card[]
}

// Helper function to convert size to grid label
function getSizeLabel(size: number | null | undefined): string {
  if (size === null || size === undefined) {
    return 'Unknown'
  }
  const sizeMap: Record<number, string> = {
    8: '4x4',
    18: '6x6',
    32: '8x8',
  }
  return sizeMap[size] || `${Math.sqrt(size * 2)}x${Math.sqrt(size * 2)}`
}

interface UserGamesResponse {
  games: Game[]
}

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
  const [userGames, setUserGames] = useState<Game[]>([])
  const [loadingGames, setLoadingGames] = useState(true)
  const [isCreatingGame, setIsCreatingGame] = useState(false)
  const [gameToDelete, setGameToDelete] = useState<number | null>(null)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  // Fetch user's games on mount and when navigating back to memory page
  useEffect(() => {
    const fetchUserGames = async () => {
      try {
        const token = authService.getAccessToken()
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        }

        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }

        const response = await fetch(`${MEMORY_SERVICE_URL}/user_games/${user?.id || 1}`, {
          headers,
        })
        if (!response.ok) throw new Error('Failed to fetch games')
        const data: UserGamesResponse = await response.json()
        setUserGames(data.games)
      } catch (err) {
        console.error('Failed to fetch user games:', err)
      } finally {
        setLoadingGames(false)
      }
    }

    // Only fetch when on the memory page (not on game sub-routes)
    if (!isGameRoute) {
      fetchUserGames()
    }
  }, [user?.id, location.pathname])

  const isGameRoute = location.pathname.startsWith('/memory/game/')

  // Reset creating game state when navigating to game route
  useEffect(() => {
    if (isGameRoute) {
      setIsCreatingGame(false)
    }
  }, [isGameRoute])

  const handleNewGame = () => {
    setShowSizePopup(true)
  }

  const handleSizeSelect = async (size: number) => {
    setShowSizePopup(false)
    setIsCreatingGame(true)
    try {
      const token = authService.getAccessToken()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${MEMORY_SERVICE_URL}/create_game`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ userId: user?.id || 1, size }),
      })
      if (!response.ok) throw new Error('Failed to create game')
      const data = await response.json()
      navigate({ to: '/memory/game/$id', params: { id: data.game.id.toString() } })
    } catch (err) {
      console.error('Failed to create game:', err)
      setIsCreatingGame(false)
    }
  }

  const handleDeleteClick = (e: React.MouseEvent, gameId: number) => {
    e.stopPropagation()
    setGameToDelete(gameId)
    setShowDeleteDialog(true)
  }

  const handleDeleteGame = async () => {
    if (gameToDelete === null) return

    try {
      const token = authService.getAccessToken()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }

      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${MEMORY_SERVICE_URL}/delete_game/${gameToDelete}`, {
        method: 'DELETE',
        headers,
      })
      if (!response.ok) throw new Error('Failed to delete game')

      // Refresh games list
      const gamesResponse = await fetch(`${MEMORY_SERVICE_URL}/user_games/${user?.id || 1}`, {
        headers,
      })
      if (!gamesResponse.ok) throw new Error('Failed to fetch games')
      const data: UserGamesResponse = await gamesResponse.json()
      setUserGames(data.games)
    } catch (err) {
      console.error('Failed to delete game:', err)
    } finally {
      setShowDeleteDialog(false)
      setGameToDelete(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto p-6">
        {!isGameRoute && (
          <>
            {/* Header */}
            <div className="text-center mb-12 animate-in fade-in slide-in-from-top-4 duration-500">
              <h1 className="text-4xl font-bold text-slate-800 mb-3">Memory Game</h1>
              <p className="text-slate-600 max-w-xl mx-auto">
                Test your memory by matching pairs of cards. Flip two cards at a time and find all matching pairs to win.
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
              <div className="grid md:grid-cols-3 gap-5">
                <div className="text-center group hover:scale-105 transition-transform duration-300">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-200 transition-colors duration-300">
                    <span className="text-blue-600 font-semibold">1</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Flip Cards</h3>
                  <p className="text-slate-500 text-sm">Click to reveal card images</p>
                </div>
                <div className="text-center group hover:scale-105 transition-transform duration-300">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-200 transition-colors duration-300">
                    <span className="text-blue-600 font-semibold">2</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Match Pairs</h3>
                  <p className="text-slate-500 text-sm">Find matching card pairs</p>
                </div>
                <div className="text-center group hover:scale-105 transition-transform duration-300">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-200 transition-colors duration-300">
                    <span className="text-blue-600 font-semibold">3</span>
                  </div>
                  <h3 className="font-medium text-slate-900 mb-1">Collect & Win</h3>
                  <p className="text-slate-500 text-sm">Collect more pairs than opponent</p>
                </div>
              </div>
            </div>

            {/* Previous Games */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-300 hover:shadow-md transition-shadow duration-300">
              <h2 className="text-lg font-semibold text-slate-900 mb-5 flex items-center gap-2">
                <Trophy size={20} className="text-amber-500" />
                Previous Games
              </h2>

              {loadingGames ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Clock size={32} className="text-slate-400 animate-pulse" />
                  </div>
                  <p className="text-slate-500 text-sm">Loading games...</p>
                </div>
              ) : userGames.length === 0 ? (
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
              ) : (
                <div className="space-y-3">
                  {userGames.map((game, index) => (
                    <div key={game.gameId} className="relative group animate-in fade-in slide-in-from-left-4 duration-300" style={{ animationDelay: `${index * 50}ms` }}>
                      <button
                        onClick={() => navigate({ to: '/memory/game/$id', params: { id: game.gameId.toString() } })}
                        className="w-full flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50 hover:scale-[1.02] transition-all duration-300 text-left group"
                      >
                        <div className="flex items-center gap-3">
                          <button
                            onClick={(e) => handleDeleteClick(e, game.gameId)}
                            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete game"
                          >
                            <Trash2 size={18} />
                          </button>
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="font-semibold text-slate-900 group-hover:text-blue-600">
                                Game #{game.gameId}
                              </span>
                              <span className="text-slate-300">•</span>
                              <span className="text-sm text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                                {getSizeLabel(game.size)}
                              </span>
                              <span className="text-slate-300">•</span>
                              <span className={`text-sm font-medium ${!game.winner || game.winner === 'none'
                                ? 'text-blue-600'
                                : game.winner === 'player1'
                                  ? 'text-green-600'
                                  : game.winner === 'player2'
                                    ? 'text-amber-600'
                                    : 'text-slate-500'
                                }`}>
                                {!game.winner || game.winner === 'none' ? 'In Progress' :
                                  game.winner === 'player1' ? 'Player 1 Won' :
                                    game.winner === 'player2' ? 'Player 2 Won' : 'Draw'}
                              </span>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <div className="flex items-center gap-1.5 text-slate-600">
                                <User size={14} />
                                <span>P1: {game.player1Cards.length}</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-600">
                                <User size={14} />
                                <span>P2: {game.player2Cards.length}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <ChevronRight size={20} className="text-slate-400 group-hover:text-blue-600 transition-colors" />
                      </button>
                    </div>
                  ))}
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
              <p className="text-slate-500 text-sm mb-4">Setting up your memory game</p>
              <div className="flex justify-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* Size Selection Popup */}
        {showSizePopup && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 animate-in fade-in duration-300">
            <div className="bg-white rounded-2xl shadow-lg p-6 max-w-md w-full animate-in slide-in-from-bottom-8 duration-300">
              <h2 className="text-xl font-semibold text-slate-900 mb-2">Select Game Size</h2>
              <p className="text-slate-500 text-sm mb-5">Choose your difficulty level</p>
              <div className="space-y-3 mb-5">
                {GAME_SIZES.map((gameSize, index) => (
                  <button
                    key={gameSize.label}
                    onClick={() => handleSizeSelect(gameSize.size)}
                    className="w-full flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50 hover:scale-[1.02] hover:shadow-md transition-all duration-300 text-left group animate-in fade-in slide-in-from-left-4 duration-300"
                    style={{ animationDelay: `${index * 75}ms` }}
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

        {/* Delete Confirmation Dialog */}
        {showDeleteDialog && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 animate-in fade-in duration-300">
            <div className="bg-white rounded-2xl shadow-lg p-6 max-w-sm w-full animate-in zoom-in-95 duration-300 hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle size={32} className="text-red-600" />
              </div>
              <h2 className="text-xl font-semibold text-slate-900 mb-2 text-center">Delete Game?</h2>
              <p className="text-slate-500 text-sm text-center mb-6">
                This action cannot be undone. The game and all its data will be permanently deleted.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteDialog(false)
                    setGameToDelete(null)
                  }}
                  className="flex-1 bg-slate-100 text-slate-700 font-medium py-2.5 px-4 rounded-lg hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteGame}
                  className="flex-1 bg-red-600 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
