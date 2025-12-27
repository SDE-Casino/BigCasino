import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from '@tanstack/react-router'
import { Trophy, RotateCcw, Clock, User, ArrowLeft, Sparkles } from 'lucide-react'
import { authService } from '../services/auth'

// Confetti component
function Confetti({ active }: { active: boolean }) {
    if (!active) return null

    const colors = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899']
    const particles = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 3,
        duration: 2 + Math.random() * 2,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 5 + Math.random() * 10,
    }))

    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-50">
            {particles.map((p) => (
                <div
                    key={p.id}
                    className="absolute animate-confetti"
                    style={{
                        left: `${p.left}%`,
                        top: '-20px',
                        width: `${p.size}px`,
                        height: `${p.size}px`,
                        backgroundColor: p.color,
                        animationDelay: `${p.delay}s`,
                        animationDuration: `${p.duration}s`,
                        borderRadius: Math.random() > 0.5 ? '50%' : '0',
                    }}
                />
            ))}
        </div>
    )
}

interface Card {
    id: number
    localId: number
    gameId: number
    flipped: boolean
    ownedBy: boolean | null
    image?: string
    kindId?: number
}

interface Game {
    id: number
    userId: number
    winner: string | null
    currentTurn: boolean
}

interface GameState {
    game: Game
    tableCards: Card[]
    player1Cards: Card[]
    player2Cards: Card[]
}

const MEMORY_SERVICE_URL = 'http://localhost:8003'

interface GameSize {
    label: string
    size: number
    cols: number
    description: string
    difficulty: 'Easy' | 'Medium' | 'Hard'
}

const GAME_SIZES: GameSize[] = [
    { label: '4x4', size: 8, cols: 4, description: 'Perfect for beginners', difficulty: 'Easy' },
    { label: '6x6', size: 18, cols: 6, description: 'A balanced challenge', difficulty: 'Medium' },
    { label: '8x8', size: 32, cols: 8, description: 'For memory masters', difficulty: 'Hard' },
]

interface MemoryGameProps {
    gameId: number
}

export default function MemoryGame({ gameId }: MemoryGameProps) {
    const { user } = useAuth()
    const navigate = useNavigate()
    const [gameState, setGameState] = useState<GameState | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isWaiting, setIsWaiting] = useState(false)
    const [showSizePopup, setShowSizePopup] = useState(false)
    const [matchedPairs, setMatchedPairs] = useState<Set<number>>(new Set())

    const loadGame = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)

            const token = authService.getAccessToken()
            const headers: HeadersInit = {
                'Content-Type': 'application/json',
            }

            if (token) {
                headers['Authorization'] = `Bearer ${token}`
            }

            const response = await fetch(`${MEMORY_SERVICE_URL}/game_status/${gameId}`, {
                headers,
            })
            if (!response.ok) throw new Error('Failed to load game')
            const data = await response.json()
            setGameState(data)

            const matched = new Set<number>()
            data.player1Cards.forEach((card: Card) => matched.add(card.kindId!))
            data.player2Cards.forEach((card: Card) => matched.add(card.kindId!))
            setMatchedPairs(matched)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load game')
        } finally {
            setLoading(false)
        }
    }, [gameId])

    const handleNewGame = () => {
        setShowSizePopup(true)
    }

    const handleBack = () => {
        navigate({ to: '/memory' })
    }

    const createGame = async (size: number = 8) => {
        try {
            setLoading(true)
            setError(null)

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
            setError(err instanceof Error ? err.message : 'Failed to create game')
            setLoading(false)
        }
    }

    const handleSizeSelect = (size: number) => {
        setShowSizePopup(false)
        createGame(size)
    }

    const flipCard = async (localId: number) => {
        if (isWaiting || !gameState) return

        try {
            const token = authService.getAccessToken()
            const headers: HeadersInit = {
                'Content-Type': 'application/json',
            }

            if (token) {
                headers['Authorization'] = `Bearer ${token}`
            }

            const response = await fetch(`${MEMORY_SERVICE_URL}/flip_card`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ game_id: gameState.game.id, local_id: localId }),
            })
            if (!response.ok) throw new Error('Failed to flip card')
            const data = await response.json()
            setGameState(data)

            const flippedCards = data.tableCards.filter((card: Card) => card.flipped)
            if (flippedCards.length === 2) {
                setIsWaiting(true)
                setTimeout(async () => {
                    await refreshGameState()
                    setIsWaiting(false)
                }, 1500)
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to flip card')
        }
    }

    const refreshGameState = async () => {
        if (!gameState) return

        try {
            const token = authService.getAccessToken()
            const headers: HeadersInit = {
                'Content-Type': 'application/json',
            }

            if (token) {
                headers['Authorization'] = `Bearer ${token}`
            }

            const response = await fetch(`${MEMORY_SERVICE_URL}/game_status/${gameState.game.id}`, {
                headers,
            })
            if (!response.ok) throw new Error('Failed to get game state')
            const data = await response.json()
            setGameState(data)

            const matched = new Set<number>()
            data.player1Cards.forEach((card: Card) => matched.add(card.kindId!))
            data.player2Cards.forEach((card: Card) => matched.add(card.kindId!))
            setMatchedPairs(matched)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to refresh game state')
        }
    }

    useEffect(() => {
        loadGame()
    }, [loadGame])

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4 animate-in fade-in duration-500">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-600 animate-pulse">Loading game...</p>
                    <div className="flex justify-center gap-2 mt-4">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
                <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-sm border border-slate-200">
                    <div className="text-center mb-6">
                        <div className="w-14 h-14 bg-red-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                            <Clock size={28} className="text-red-500" />
                        </div>
                        <h1 className="text-xl font-semibold text-slate-900 mb-2">Error</h1>
                        <p className="text-slate-500">{error}</p>
                    </div>
                    <button
                        type="button"
                        onClick={() => loadGame()}
                        className="w-full bg-blue-600 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        )
    }

    if (!gameState) {
        return null
    }

    const { game, tableCards, player1Cards, player2Cards } = gameState

    const getGridCols = (totalCards: number): number => {
        if (totalCards <= 16) return 4
        if (totalCards <= 36) return 6
        return 8
    }

    const gridCols = getGridCols(tableCards.length + player1Cards.length + player2Cards.length)

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
            <div className="max-w-4xl mx-auto p-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
                    <div>
                        <button
                            onClick={handleBack}
                            className="inline-flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors mb-2 text-sm"
                        >
                            <ArrowLeft size={16} />
                            Back
                        </button>
                        <h1 className="text-3xl font-bold text-slate-800">Memory Game</h1>
                    </div>
                    <button
                        type="button"
                        onClick={handleNewGame}
                        className="flex items-center gap-2 bg-blue-600 text-white font-medium py-2.5 px-5 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <RotateCcw size={18} />
                        New Game
                    </button>
                </div>

                {/* Winner Banner */}
                {game.winner && (
                    <>
                        <Confetti active={true} />
                        <div className="p-6 bg-amber-50 rounded-2xl border border-amber-200 text-center animate-in fade-in zoom-in-95 duration-500">
                            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mx-auto mb-3 animate-bounce">
                                <Trophy size={24} className="text-amber-600" />
                            </div>
                            <h2 className="text-xl font-semibold text-slate-900 mb-1">
                                {game.winner === 'draw' ? "It's a Draw!" : `${game.winner === 'player1' ? 'Player 1' : 'Player 2'} Wins!`}
                            </h2>
                            <p className="text-slate-500 text-sm">Game completed</p>
                        </div>
                    </>
                )}

                {/* Turn Indicator */}
                <div className="mb-8 p-4 bg-white rounded-xl shadow-sm border border-slate-200">
                    <div className="flex items-center justify-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${!game.currentTurn ? 'bg-blue-600 animate-pulse' : 'bg-slate-300'}`}></div>
                        <h2 className="text-lg font-medium text-slate-900">
                            Current Turn: <span className={`font-semibold ${game.currentTurn ? 'text-purple-600' : 'text-blue-600'}`}>
                                {game.currentTurn ? 'Player 2' : 'Player 1'}
                            </span>
                        </h2>
                        <div className={`w-3 h-3 rounded-full ${game.currentTurn ? 'bg-purple-600 animate-pulse' : 'bg-slate-300'}`}></div>
                    </div>
                </div>

                {/* Game Board */}
                <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 mb-8">
                    <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))` }}>
                        {Array.from({ length: tableCards.length + player1Cards.length + player2Cards.length }, (_, index) => {
                            const card = tableCards.find((c) => c.localId === index)
                            return (
                                <div
                                    key={index}
                                    className="aspect-square"
                                >
                                    {card ? (
                                        <button
                                            type="button"
                                            onClick={() => flipCard(card.localId)}
                                            disabled={card.flipped || isWaiting}
                                            className={`relative w-full h-full rounded-xl shadow-sm border-2 overflow-hidden transition-transform duration-200 ${card.flipped
                                                ? 'bg-white border-slate-200'
                                                : 'border-transparent cursor-pointer hover:scale-105'
                                                } ${isWaiting ? 'cursor-not-allowed' : ''}`}
                                            style={{
                                                '--card-color-1': game.currentTurn ? '#a855f7' : '#3b82f6',
                                                '--card-color-2': game.currentTurn ? '#9333ea' : '#2563eb',
                                                '--card-hover-color-1': game.currentTurn ? '#9333ea' : '#2563eb',
                                                '--card-hover-color-2': game.currentTurn ? '#7e22ce' : '#1d4ed8',
                                                background: card.flipped ? 'white' : 'linear-gradient(135deg, var(--card-color-1), var(--card-color-2))',
                                                transition: card.flipped ? 'none' : 'transform 0.2s, --card-color-1 0.5s ease, --card-color-2 0.5s ease, --card-hover-color-1 0.5s ease, --card-hover-color-2 0.5s ease'
                                            } as React.CSSProperties}
                                            onMouseEnter={(e) => {
                                                if (!card.flipped) {
                                                    e.currentTarget.style.background = 'linear-gradient(135deg, var(--card-hover-color-1), var(--card-hover-color-2))'
                                                }
                                            }}
                                            onMouseLeave={(e) => {
                                                if (!card.flipped) {
                                                    e.currentTarget.style.background = 'linear-gradient(135deg, var(--card-color-1), var(--card-color-2))'
                                                }
                                            }}
                                        >
                                            <div className={`absolute inset-0 flex items-center justify-center ${card.flipped && card.image ? 'opacity-0' : 'opacity-100'}`}>
                                                <span className="text-white text-3xl font-medium pointer-events-none">?</span>
                                            </div>
                                            {card.flipped && card.image ? (
                                                <>
                                                    <img
                                                        src={`data:image/jpeg;base64,${card.image}`}
                                                        alt="Card"
                                                        className="absolute inset-0 w-full h-full object-cover"
                                                    />
                                                    <div className={`absolute inset-0 bg-green-500/80 flex items-center justify-center transition-opacity duration-200 ${matchedPairs.has(card.kindId!) ? 'opacity-100' : 'opacity-0'}`}>
                                                        <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                                                            <div className="w-4 h-1 bg-green-500 rounded-full"></div>
                                                        </div>
                                                    </div>
                                                </>
                                            ) : null}
                                        </button>
                                    ) : (
                                        <div className="w-full h-full rounded-xl bg-slate-50 border border-dashed border-slate-200 opacity-50"></div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* Player Scores */}
                <div className="grid grid-cols-2 gap-4 mb-8">
                    <div className={`p-5 rounded-xl border-2 transition-all duration-500 ease-in-out ${!game.currentTurn ? 'bg-white border-blue-500 shadow-md shadow-blue-500/20' : 'bg-white border-slate-200'}`}>
                        <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-500 ease-in-out ${!game.currentTurn ? 'bg-blue-500 scale-110' : 'bg-slate-100'}`}>
                                <User size={20} className={`transition-colors duration-500 ${!game.currentTurn ? 'text-white' : 'text-slate-600'}`} />
                            </div>
                            <div className="flex-1">
                                <h3 className="font-medium text-slate-900">Player 1</h3>
                                <p className="text-slate-500 text-sm">Pairs</p>
                            </div>
                            <div className={`text-3xl font-bold transition-colors duration-500 ${!game.currentTurn ? 'text-blue-600 scale-110' : 'text-slate-400'}`}>
                                {player1Cards.length}
                            </div>
                        </div>
                    </div>
                    <div className={`p-5 rounded-xl border-2 transition-all duration-500 ease-in-out ${game.currentTurn ? 'bg-white border-purple-500 shadow-md shadow-purple-500/20' : 'bg-white border-slate-200'}`}>
                        <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-500 ease-in-out ${game.currentTurn ? 'bg-purple-500 scale-110' : 'bg-slate-100'}`}>
                                <User size={20} className={`transition-colors duration-500 ${game.currentTurn ? 'text-white' : 'text-slate-600'}`} />
                            </div>
                            <div className="flex-1">
                                <h3 className="font-medium text-slate-900">Player 2</h3>
                                <p className="text-slate-500 text-sm">Pairs</p>
                            </div>
                            <div className={`text-3xl font-bold transition-colors duration-500 ${game.currentTurn ? 'text-purple-600 scale-110' : 'text-slate-400'}`}>
                                {player2Cards.length}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Waiting Indicator - Fixed height container to prevent layout shift */}
                <div className="mb-8 min-h-[52px]">
                    {isWaiting && (
                        <div className="p-4 bg-blue-50 rounded-xl text-center border border-blue-100">
                            <div className="flex items-center justify-center gap-3">
                                <div className="w-5 h-5 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin"></div>
                                <p className="text-slate-600 text-sm">Waiting for cards to flip back...</p>
                            </div>
                        </div>
                    )}
                </div>

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
                                        type="button"
                                        onClick={() => handleSizeSelect(gameSize.size)}
                                        className="w-full flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50 transition-colors text-left"
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
                                type="button"
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
