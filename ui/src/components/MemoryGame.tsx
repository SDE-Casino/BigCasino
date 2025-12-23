import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'

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
}

const GAME_SIZES: GameSize[] = [
    { label: '4x4', size: 8, cols: 4 },
    { label: '6x6', size: 18, cols: 6 },
    { label: '8x8', size: 32, cols: 8 },
]

interface MemoryGameProps {
    initialSize?: number
}

export default function MemoryGame({ initialSize }: MemoryGameProps) {
    const { user } = useAuth()
    const [gameState, setGameState] = useState<GameState | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isWaiting, setIsWaiting] = useState(false)
    const [showSizePopup, setShowSizePopup] = useState(false)

    const createGame = useCallback(async (size: number = 8) => {
        try {
            setLoading(true)
            setError(null)

            const response = await fetch(`${MEMORY_SERVICE_URL}/create_game`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: user?.id || 1, size }),
            })
            if (!response.ok) throw new Error('Failed to create game')
            const data = await response.json()
            setGameState(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create game')
        } finally {
            setLoading(false)
        }
    }, [user])

    const handleNewGame = () => {
        setShowSizePopup(true)
    }

    const handleSizeSelect = (size: number) => {
        setShowSizePopup(false)
        createGame(size)
    }

    const flipCard = async (localId: number) => {
        if (isWaiting || !gameState) return

        try {
            const response = await fetch(`${MEMORY_SERVICE_URL}/flip_card`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            const response = await fetch(`${MEMORY_SERVICE_URL}/game_status/${gameState.game.id}`)
            if (!response.ok) throw new Error('Failed to get game state')
            const data = await response.json()
            setGameState(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to refresh game state')
        }
    }

    useEffect(() => {
        if (initialSize) {
            createGame(initialSize)
        } else {
            createGame()
        }
    }, [createGame, initialSize])

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-100 to-teal-100 p-4">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading game...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-green-100 to-teal-100 p-4">
                <div className="w-full max-w-md p-8 rounded-xl backdrop-blur-md bg-white/50 shadow-xl border border-white/20">
                    <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Error</h1>
                    <p className="text-center text-red-600 mb-6">{error}</p>
                    <button
                        type="button"
                        onClick={() => createGame()}
                        className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-600 hover:to-teal-700 transition-all duration-300"
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

    // Calculate grid columns based on game size
    // Backend creates 2*size cards, so we check against total cards
    const getGridCols = (totalCards: number): number => {
        if (totalCards <= 16) return 4   // size=8 → 16 cards → 4x4
        if (totalCards <= 36) return 6   // size=18 → 36 cards → 6x6
        return 8                          // size=32 → 64 cards → 8x8
    }

    const gridCols = getGridCols(tableCards.length + player1Cards.length + player2Cards.length)

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-100 to-teal-100 p-4">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold text-gray-800">Memory Game</h1>
                    <button
                        type="button"
                        onClick={handleNewGame}
                        className="bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-2 px-4 rounded-lg hover:from-green-600 hover:to-teal-700 transition-all duration-300"
                    >
                        New Game
                    </button>
                </div>

                {game.winner && (
                    <div className="mb-6 p-4 rounded-xl bg-white/70 backdrop-blur-sm shadow-lg text-center">
                        <h2 className="text-2xl font-bold text-gray-800">
                            {game.winner === 'draw' ? "It's a draw!" : `${game.winner === 'player1' ? 'Player 1' : 'Player 2'} wins!`}
                        </h2>
                    </div>
                )}

                <div className="mb-6 p-4 rounded-xl bg-white/70 backdrop-blur-sm shadow-lg text-center">
                    <h2 className="text-xl font-bold text-gray-800">
                        Current Turn: <span className={game.currentTurn ? 'text-blue-600' : 'text-purple-600'}>
                            {game.currentTurn ? 'Player 2' : 'Player 1'}
                        </span>
                    </h2>
                </div>

                <div className="grid gap-4 mb-6" style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))` }}>
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
                                        className={`w-full h-full rounded-xl shadow-lg transition-all duration-300 ${card.flipped
                                            ? 'bg-white border-4 border-green-400'
                                            : 'bg-gradient-to-br from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 cursor-pointer'
                                            } ${isWaiting ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                        {card.flipped && card.image ? (
                                            <img
                                                src={`data:image/jpeg;base64,${card.image}`}
                                                alt="Card"
                                                className="w-full h-full object-cover rounded-lg"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <span className="text-white text-4xl">?</span>
                                            </div>
                                        )}
                                    </button>
                                ) : (
                                    <div className="w-full h-full rounded-xl bg-transparent border-2 border-dashed border-gray-300 opacity-30"></div>
                                )}
                            </div>
                        )
                    })}
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-white/70 backdrop-blur-sm shadow-lg">
                        <h3 className="text-lg font-bold text-gray-800 mb-2">Player 1</h3>
                        <p className="text-gray-600">Cards: {player1Cards.length}</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/70 backdrop-blur-sm shadow-lg">
                        <h3 className="text-lg font-bold text-gray-800 mb-2">Player 2</h3>
                        <p className="text-gray-600">Cards: {player2Cards.length}</p>
                    </div>
                </div>

                {isWaiting && (
                    <div className="mt-4 p-4 rounded-xl bg-yellow-100 border border-yellow-300 text-center">
                        <p className="text-yellow-800">Waiting for cards to flip back...</p>
                    </div>
                )}

                {showSizePopup && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Select Game Size</h2>
                            <div className="grid grid-cols-2 gap-4">
                                {GAME_SIZES.map((gameSize) => (
                                    <button
                                        key={gameSize.label}
                                        type="button"
                                        onClick={() => handleSizeSelect(gameSize.size)}
                                        className="bg-gradient-to-r from-green-500 to-teal-600 text-white font-bold py-4 px-6 rounded-xl hover:from-green-600 hover:to-teal-700 transition-all duration-300 text-xl"
                                    >
                                        {gameSize.label}
                                    </button>
                                ))}
                            </div>
                            <button
                                type="button"
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