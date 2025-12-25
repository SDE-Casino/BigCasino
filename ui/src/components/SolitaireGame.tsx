import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Trophy, RotateCcw, ArrowLeft, RefreshCw, Sparkles, XCircle, AlertCircle } from 'lucide-react'

const SOLITAIRE_SERVICE_URL = 'http://localhost:8005'

// Toast notification component
interface ToastProps {
  message: string
  type: 'error' | 'warning'
  onClose: () => void
}

function Toast({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-5 border border-slate-200 animate-in fade-in slide-in-from-bottom-4 duration-300 max-w-md w-full">
      <div className="flex items-start gap-4">
        {type === 'error' ? (
          <XCircle size={24} className="text-red-500 flex-shrink-0 mt-0.5" />
        ) : (
          <AlertCircle size={24} className="text-amber-500 flex-shrink-0 mt-0.5" />
        )}
        <p className="text-slate-700 text-base flex-1">{message}</p>
        <button
          type="button"
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 transition-colors"
        >
          <XCircle size={18} />
        </button>
      </div>
    </div>
  )
}

// Import game states from parent route
// @ts-ignore
const getGameStates = () => (window as any).__solitaireGameStates || {}
// @ts-ignore
const storeGameState = (gameId: string, state: any) => {
  if (!(window as any).__solitaireGameStates) {
    ; (window as any).__solitaireGameStates = {}
  }
  ; (window as any).__solitaireGameStates[gameId] = state
}

// Preload all card images from game state
const preloadCardImages = async (gameState: any): Promise<void> => {
  const imageUrls = new Set<string>()

  // Collect all unique image URLs from the game state
  const collectImages = (cards: any[]) => {
    cards.forEach(card => {
      if (typeof card === 'object' && card !== null) {
        // Handle card tuples [card, faceUp]
        if (Array.isArray(card)) {
          const cardObj = card[0]
          if (cardObj?.image) {
            imageUrls.add(cardObj.image)
          }
        } else if (card.image) {
          // Handle plain card objects
          imageUrls.add(card.image)
        }
      }
    })
  }

  // Collect images from all piles
  if (gameState?.tableau) {
    gameState.tableau.forEach((column: any[]) => collectImages(column))
  }
  if (gameState?.stock) {
    collectImages(gameState.stock)
  }
  if (gameState?.talon) {
    collectImages(gameState.talon)
  }
  if (gameState?.foundation) {
    Object.values(gameState.foundation).forEach((pile: unknown) => {
      if (Array.isArray(pile)) {
        collectImages(pile)
      }
    })
  }

  // Preload all images
  const preloadPromises = Array.from(imageUrls).map(url => {
    return new Promise<void>((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve()
      img.onerror = () => resolve() // Resolve even on error to not block the game
      img.src = url
    })
  })

  await Promise.all(preloadPromises)
}

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

// Card component
interface CardProps {
  card: { value: string; suit: string; image?: string }
  faceUp: boolean
  selected: boolean
  onClick: () => void
}

function Card({ card, faceUp, selected, onClick }: CardProps) {
  if (!faceUp) {
    return (
      <div
        onClick={onClick}
        className="w-full h-full rounded-lg bg-gradient-to-br from-blue-600 to-blue-800 shadow-md border-2 border-blue-900 cursor-pointer hover:scale-105 transition-transform duration-200"
      >
        <div className="w-full h-full rounded-lg bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEwIDBMMjAgMTBIMTBMMjAgMjBIMTBMMCAxMEgxMEwwIDBIMTB6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiLz48L3N2Zz4=')] bg-repeat opacity-50"></div>
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full h-full rounded-lg shadow-md border-2 cursor-pointer transition-all duration-200 overflow-hidden ${selected
        ? 'border-yellow-400 ring-4 ring-yellow-400/50 scale-105'
        : 'border-slate-300 hover:scale-105 hover:shadow-lg'
        } bg-white relative`}
    >
      {card.image ? (
        <img
          src={card.image}
          alt={`${card.value} of ${card.suit}`}
          className="w-full h-full object-cover"
        />
      ) : (
        // Fallback to custom rendering if image is not available
        <div className="w-full h-full flex flex-col items-center justify-center p-2">
          <span className="text-lg font-bold">{card.value}</span>
          <span className="text-2xl">{card.suit[0]}</span>
        </div>
      )}
    </button>
  )
}

interface SolitaireGameProps {
  gameId: string
}

export default function SolitaireGame({ gameId }: SolitaireGameProps) {
  const navigate = useNavigate()
  const [gameState, setGameState] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'warning' } | null>(null)
  const [selectedCard, setSelectedCard] = useState<{
    card: { value: string; suit: string }
    source: 'tableau' | 'talon' | 'foundation'
    sourceIndex: number
    cardIndex?: number
  } | null>(null)
  const [won, setWon] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const showToast = useCallback((message: string, type: 'error' | 'warning' = 'error') => {
    setToast({ message, type })
  }, [])

  const loadGame = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Try to get stored game state first
      const storedStates = getGameStates()
      const storedState = storedStates[gameId]

      if (storedState) {
        // Preload card images
        await preloadCardImages(storedState)
        setGameState(storedState)
        setLoading(false)
        return
      }

      // If no stored state, show error (we can't fetch game state from API)
      setError('Game not found. Please start a new game from the main page.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load game')
    } finally {
      setLoading(false)
    }
  }, [gameId])

  const handleBack = () => {
    navigate({ to: '/solitaire' })
  }

  const handleNewGame = async () => {
    setIsProcessing(true)
    try {
      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/create_game`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      console.log(response)
      if (!response.ok) throw new Error('Failed to create game')
      const data = await response.json()

      // Preload card images
      await preloadCardImages(data.game_state)

      setGameState(data.game_state)
      setWon(false)
      setSelectedCard(null)
      // Store new game state
      storeGameState(gameId, data.game_state)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDrawCards = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    try {
      console.log('Drawing cards. Current talon before:', gameState?.talon)
      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/draw_cards/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!response.ok) throw new Error('Failed to draw cards')
      const data = await response.json()
      console.log('Draw cards response:', data)
      console.log('New talon after draw:', data.game_state.talon)
      setGameState(data.game_state)
      // Clear selected card when drawing new cards, as the talon has changed
      setSelectedCard(null)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to draw cards', 'warning')
      setSelectedCard(null)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleResetStock = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    try {
      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/reset_stock/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!response.ok) throw new Error('Failed to reset stock')
      const data = await response.json()
      setGameState(data.game_state)
      // Clear selected card when resetting stock, as the talon has changed
      setSelectedCard(null)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to reset stock', 'warning')
      setSelectedCard(null)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleCardClick = async (
    card: { value: string; suit: string },
    source: 'tableau' | 'talon' | 'foundation',
    sourceIndex: number,
    cardIndex?: number
  ) => {
    if (isProcessing || won) return

    console.log('Card clicked:', { card, source, sourceIndex, cardIndex })
    console.log('Current selectedCard:', selectedCard)
    console.log('Current talon:', gameState?.talon)

    // If no card is selected, select this card
    if (!selectedCard) {
      setSelectedCard({ card, source, sourceIndex, cardIndex })
      console.log('Selected card:', { card, source, sourceIndex, cardIndex })
      return
    }

    // If clicking the same card, deselect it
    // Compare card properties instead of object reference to handle state updates
    const isSameCard =
      selectedCard.card.value === card.value &&
      selectedCard.card.suit === card.suit &&
      selectedCard.source === source &&
      selectedCard.sourceIndex === sourceIndex &&
      selectedCard.cardIndex === cardIndex

    if (isSameCard) {
      console.log('Deselecting card')
      setSelectedCard(null)
      return
    }

    // Try to move the selected card to the clicked destination
    await handleMove(selectedCard, { card, source, sourceIndex, cardIndex })
  }

  const handleMove = async (
    from: { card: { value: string; suit: string }; source: 'tableau' | 'talon' | 'foundation'; sourceIndex: number; cardIndex?: number },
    to: { card: { value: string; suit: string }; source: 'tableau' | 'talon' | 'foundation'; sourceIndex: number; cardIndex?: number }
  ) => {
    setIsProcessing(true)
    try {
      let body: any = {}

      // Build the request body based on source and destination
      if (from.source === 'tableau' && to.source === 'tableau') {
        // Calculate number of cards from the clicked card to the end of the column
        const fromColumn = gameState.tableau[from.sourceIndex]
        const numberOfCards = from.cardIndex !== undefined ? fromColumn.length - from.cardIndex : 1
        body = {
          column_from: from.sourceIndex,
          column_to: to.sourceIndex,
          number_of_cards: numberOfCards,
        }
      } else if (from.source === 'tableau' && to.source === 'foundation') {
        body = {
          column_from: from.sourceIndex,
          suit: to.card.suit,
        }
      } else if (from.source === 'talon' && to.source === 'tableau') {
        body = {
          column_to: to.sourceIndex,
        }
      } else if (from.source === 'talon' && to.source === 'foundation') {
        body = {
          suit: to.card.suit,
        }
      } else {
        // Invalid move combination
        setSelectedCard(null)
        setIsProcessing(false)
        return
      }

      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/move_card/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to move card')
      }

      const data = await response.json()
      setGameState(data.game_state)
      // Update stored game state
      storeGameState(gameId, data.game_state)
      setSelectedCard(null)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to move card', 'warning')
      setSelectedCard(null)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleFoundationClick = async (suit: string) => {
    if (isProcessing || won) return

    // If no card is selected, do nothing
    if (!selectedCard) return

    // Try to move the selected card to this foundation
    setIsProcessing(true)
    try {
      let body: any = {}

      if (selectedCard.source === 'tableau') {
        body = {
          column_from: selectedCard.sourceIndex,
          suit: suit,
        }
      } else if (selectedCard.source === 'talon') {
        body = {
          suit: suit,
        }
      } else {
        setSelectedCard(null)
        setIsProcessing(false)
        return
      }

      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/move_card/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to move card')
      }

      const data = await response.json()
      setGameState(data.game_state)
      // Update stored game state
      storeGameState(gameId, data.game_state)
      setSelectedCard(null)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to move card', 'warning')
      setSelectedCard(null)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleEmptyTableauClick = async (columnIndex: number) => {
    if (isProcessing || won) return

    // If no card is selected, do nothing
    if (!selectedCard) return

    // Try to move the selected card to this empty column
    setIsProcessing(true)
    try {
      let body: any = {}

      if (selectedCard.source === 'tableau') {
        // Calculate number of cards from the clicked card to the end of the column
        const fromColumn = gameState.tableau[selectedCard.sourceIndex]
        const numberOfCards = selectedCard.cardIndex !== undefined ? fromColumn.length - selectedCard.cardIndex : 1
        body = {
          column_from: selectedCard.sourceIndex,
          column_to: columnIndex,
          number_of_cards: numberOfCards,
        }
      } else if (selectedCard.source === 'talon') {
        body = {
          column_to: columnIndex,
        }
      } else {
        setSelectedCard(null)
        setIsProcessing(false)
        return
      }

      const response = await fetch(`${SOLITAIRE_SERVICE_URL}/move_card/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to move card')
      }

      const data = await response.json()
      setGameState(data.game_state)
      // Update stored game state
      storeGameState(gameId, data.game_state)
      setSelectedCard(null)
      if (data.game_status === 'won') {
        setWon(true)
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to move card', 'warning')
      setSelectedCard(null)
    } finally {
      setIsProcessing(false)
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
          <p className="text-slate-600 animate-pulse">Loading game and preloading card images...</p>
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
              <RotateCcw size={28} className="text-red-500" />
            </div>
            <h1 className="text-xl font-semibold text-slate-900 mb-2">Error</h1>
            <p className="text-slate-500">{error}</p>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setError(null)}
              className="flex-1 bg-blue-600 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!gameState) {
    return null
  }

  const { tableau, foundation, stock, talon } = gameState

  const suitSymbols: Record<string, string> = {
    HEARTS: '♥',
    DIAMONDS: '♦',
    CLUBS: '♣',
    SPADES: '♠',
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Confetti active={won} />
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      <div className="max-w-6xl mx-auto p-4">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <button
              onClick={handleBack}
              className="inline-flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors mb-2 text-sm"
            >
              <ArrowLeft size={16} />
              Back
            </button>
            <h1 className="text-3xl font-bold text-slate-800">Solitaire</h1>
          </div>
        </div>

        {/* Winner Banner */}
        {won && (
          <div className="mb-6 p-6 bg-amber-50 rounded-2xl border border-amber-200 text-center animate-in fade-in zoom-in-95 duration-500">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mx-auto mb-3 animate-bounce">
              <Trophy size={24} className="text-amber-600" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 mb-1">Congratulations!</h2>
            <p className="text-slate-500 text-sm">You've won the game!</p>
          </div>
        )}

        {/* Stock, Talon, and Foundation */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Stock */}
            <div className="flex items-center gap-4">
              <div className="w-20 h-28">
                {stock.length > 0 ? (
                  <button
                    type="button"
                    onClick={handleDrawCards}
                    disabled={isProcessing}
                    className="w-full h-full rounded-lg bg-gradient-to-br from-blue-600 to-blue-800 shadow-md border-2 border-blue-900 cursor-pointer hover:scale-105 transition-transform duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <div className="w-full h-full rounded-lg bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEwIDBMMjAgMTBIMTBMMjAgMjBIMTBMMCAxMEgxMEwwIDBIMTB6IiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiLz48L3N2Zz4=')] bg-repeat opacity-50"></div>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleResetStock}
                    disabled={isProcessing || talon.length === 0}
                    className="w-full h-full rounded-lg bg-slate-100 border-2 border-dashed border-slate-300 flex items-center justify-center hover:bg-slate-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RefreshCw size={24} className="text-slate-400" />
                  </button>
                )}
              </div>
              <div className="text-slate-500 text-sm">
                <p className="font-medium">Stock</p>
                <p>{stock.length} cards</p>
              </div>
            </div>

            {/* Talon - shows up to 3 cards stacked, all selectable */}
            <div className="flex items-center gap-4">
              <div className="text-slate-500 text-sm">
                <p className="font-medium">Talon</p>
                <p>{talon.length} cards</p>
              </div>
              <div className="relative w-48 h-28">
                {talon.length > 0 && (
                  <>
                    {/* Show up to 3 cards stacked with more visibility */}
                    {talon.slice(-3).map((card: any, index: number) => {
                      const actualIndex = talon.length - 3 + index
                      const isTopCard = actualIndex === talon.length - 1
                      const isSelected = selectedCard?.source === 'talon' && selectedCard.sourceIndex === actualIndex
                      return (
                        <div
                          key={actualIndex}
                          className={`absolute ${index === 0 ? 'z-10' : index === 1 ? 'z-20' : 'z-30'}`}
                          style={{
                            left: `${index * 40}px`,
                          }}
                        >
                          <button
                            type="button"
                            onClick={() => handleCardClick(card, 'talon', actualIndex)}
                            disabled={isProcessing}
                            className="w-20 h-28"
                          >
                            <Card
                              card={card}
                              faceUp={true}
                              selected={isSelected}
                              onClick={() => { }}
                            />
                          </button>
                        </div>
                      )
                    })}
                  </>
                )}
              </div>
            </div>

            {/* Foundations */}
            <div className="flex gap-3">
              {(['HEARTS', 'DIAMONDS', 'CLUBS', 'SPADES'] as const).map((suit) => (
                <button
                  key={suit}
                  type="button"
                  onClick={() => handleFoundationClick(suit)}
                  disabled={isProcessing}
                  className={`w-20 h-28 rounded-lg border-2 flex flex-col items-center justify-center transition-all duration-200 ${selectedCard ? 'hover:bg-slate-50 cursor-pointer' : 'cursor-default'
                    } ${foundation[suit].length > 0
                      ? 'bg-white border-slate-300'
                      : 'bg-slate-100 border-dashed border-slate-300'
                    }`}
                >
                  {foundation[suit].length > 0 ? (
                    <Card
                      card={foundation[suit][foundation[suit].length - 1]}
                      faceUp={true}
                      selected={false}
                      onClick={() => { }}
                    />
                  ) : (
                    <span className={`text-3xl ${suit === 'HEARTS' || suit === 'DIAMONDS' ? 'text-red-600' : 'text-slate-800'}`}>
                      {suitSymbols[suit]}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tableau */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200">
          <div className="grid grid-cols-7 gap-3">
            {tableau.map((column: any[], columnIndex: number) => (
              <div key={columnIndex} className="flex flex-col items-center gap-1">
                <div
                  className="w-20 h-28 rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-slate-100 transition-colors"
                  onClick={() => handleEmptyTableauClick(columnIndex)}
                />
                <div className="flex flex-col gap-1 -mt-20">
                  {column.map((cardTuple: [any, boolean], cardIndex: number) => {
                    const [card, faceUp] = cardTuple
                    const isSelected =
                      selectedCard?.source === 'tableau' &&
                      selectedCard.sourceIndex === columnIndex &&
                      selectedCard.cardIndex === cardIndex
                    return (
                      <div
                        key={cardIndex}
                        className="w-20"
                        style={{ marginTop: cardIndex > 0 ? '-80px' : '0' }}
                      >
                        {faceUp ? (
                          <button
                            type="button"
                            onClick={() => handleCardClick(card, 'tableau', columnIndex, cardIndex)}
                            disabled={isProcessing}
                            className="w-full h-28"
                          >
                            <Card
                              card={card}
                              faceUp={faceUp}
                              selected={isSelected}
                              onClick={() => { }}
                            />
                          </button>
                        ) : (
                          <div className="w-full h-28">
                            <Card
                              card={card}
                              faceUp={faceUp}
                              selected={false}
                              onClick={() => { }}
                            />
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="fixed bottom-4 right-4 bg-white rounded-xl shadow-lg p-4 border border-slate-200 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin"></div>
              <p className="text-slate-600 text-sm">Processing...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
