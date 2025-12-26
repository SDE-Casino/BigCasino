import { createFileRoute, redirect } from '@tanstack/react-router'
import SolitaireGame from '../../../components/SolitaireGame'

export const Route = createFileRoute('/solitaire/game/$id')({
    component: SolitaireGameRoute,
    loader: async ({ params }) => {
        const gameId = params.id
        if (!gameId) {
            throw redirect({ to: '/solitaire' })
        }
        return { gameId }
    },
})

function SolitaireGameRoute() {
    const { gameId } = Route.useLoaderData()
    return <SolitaireGame gameId={gameId} />
}
