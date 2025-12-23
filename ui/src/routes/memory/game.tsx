import { createFileRoute } from '@tanstack/react-router'
import MemoryGame from '../../components/MemoryGame'

export const Route = createFileRoute('/memory/game')({
    component: MemoryGameRoute,
})

function MemoryGameRoute() {
    return <MemoryGame />
}