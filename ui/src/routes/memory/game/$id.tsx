import { createFileRoute, redirect } from '@tanstack/react-router'
import MemoryGame from '../../../components/MemoryGame'

export const Route = createFileRoute('/memory/game/$id')({
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
    component: MemoryGameRoute,
    loader: async ({ params }) => {
        const gameId = parseInt(params.id)
        if (isNaN(gameId)) {
            throw redirect({ to: '/memory' })
        }
        return { gameId }
    },
})

function MemoryGameRoute() {
    const { gameId } = Route.useLoaderData()
    return <MemoryGame gameId={gameId} />
}
