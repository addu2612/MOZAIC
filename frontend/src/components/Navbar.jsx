import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/AuthContext'

export default function Navbar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-3 py-1 text-xs font-semibold ring-1 ring-blue-500/30">
              MOZAIC
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-slate-200 hover:text-white font-semibold"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}