import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'
import { Gamepad2, Dices } from 'lucide-react'

export const Route = createFileRoute('/')({
  component: App,
})

function App() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    throw redirect({ to: '/auth' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-12 text-gray-800">
          Welcome to Big Casino
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Link
            to="/memory"
            className="group bg-white/70 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 border border-white/50"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-teal-500 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Gamepad2 size={40} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Memory Game
              </h2>
              <p className="text-gray-600">
                Test your memory skills with this classic card matching game
              </p>
            </div>
          </Link>

          <Link
            to="/solitaire"
            className="group bg-white/70 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 border border-white/50"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-red-400 to-orange-500 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Dices size={40} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Solitaire
              </h2>
              <p className="text-gray-600">
                Play the classic card game and challenge yourself
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
