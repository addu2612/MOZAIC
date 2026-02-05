import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './utils/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProjectDetail from './pages/ProjectDetail'
import ConnectAccount from './pages/ConnectAccount'
import Navbar from './components/Navbar'

function ProtectedRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" />
}

function App() {
  const { token } = useAuth()

  return (
    <BrowserRouter>
      {token && <Navbar />}
      <Routes>
        <Route path="/login" element={token ? <Navigate to="/" /> : <Login />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/project/:id" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>} />
        <Route path="/project/:id/connect" element={<ProtectedRoute><ConnectAccount /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App