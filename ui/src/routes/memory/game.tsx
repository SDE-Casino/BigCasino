import { createFileRoute } from '@tanstack/react-router'
import MemoryGame from '../../components/MemoryGame'

export const Route = createFileRoute('/memory/game')({
    component: MemoryGameRoute,
    validateSearch: (search: Record<string, unknown>) => ({
        size: typeof search.size === 'number' ? search.size : typeof search.size === 'string' ? parseInt(search.size) : 8,
    }),
})

function MemoryGameRoute() {
    const { size } = Route.useSearch()
    return <MemoryGame initialSize={size} />
}