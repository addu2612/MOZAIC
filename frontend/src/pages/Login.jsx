import { useState } from 'react'
import { useAuth } from '../utils/AuthContext'
import api from '../utils/api'

export default function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register'
      const { data } = await api.post(endpoint, { email, password })
      
      if (isLogin) {
        login(data.access_token)
      } else {
        setIsLogin(true)
        setError('Registration successful! Please login.')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.25),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(16,185,129,0.18),_transparent_40%)]" />
      <div className="relative z-10 min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 lg:p-10 shadow-2xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-3 py-1 text-xs font-semibold ring-1 ring-blue-500/30">
              Secure Access
            </div>
            <h1 className="text-4xl font-bold mt-6">MOZAIC</h1>
            <p className="text-slate-300 mt-3 text-sm">Multi-Source Orchestrated Anomaly Coordinator</p>

            <div className="mt-8 space-y-4 text-sm text-slate-300">
              <div className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-400" />
                <div>
                  <div className="font-semibold text-white">Unified signal intake</div>
                  <div>Aggregate incidents from Sentry, Grafana, CloudWatch, and Kubernetes.</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-blue-400" />
                <div>
                  <div className="font-semibold text-white">Clustered insights</div>
                  <div>Surface root causes, severity, and evidence in seconds.</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-purple-400" />
                <div>
                  <div className="font-semibold text-white">Action-ready output</div>
                  <div>Generate resolution steps and next actions for your teams.</div>
                </div>
              </div>
            </div>

            <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="text-xs uppercase tracking-wide text-slate-400">Status</div>
              <div className="mt-2 flex items-center gap-2 text-sm">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                <span className="text-slate-200">All systems operational</span>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-white/95 text-slate-900 p-8 lg:p-10 shadow-2xl">
            <div className="text-sm text-slate-500">Welcome back</div>
            <h2 className="text-2xl font-bold mt-2">{isLogin ? 'Sign in to your workspace' : 'Create your workspace'}</h2>
            <p className="text-sm text-slate-600 mt-2">Use your email and password to continue.</p>
        
            {error && (
              <div className={`mt-5 mb-4 p-3 rounded-lg text-sm ${error.includes('successful') ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200' : 'bg-red-50 text-red-700 ring-1 ring-red-200'}`}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-200 rounded-xl bg-white text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                  placeholder="name@company.com"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-200 rounded-xl bg-white text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                  placeholder="••••••••"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-slate-900 text-white py-3 rounded-xl font-semibold hover:bg-slate-800 transition disabled:opacity-50 disabled:hover:bg-slate-900"
              >
                {loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}
              </button>
            </form>

            <div className="mt-6 flex items-center justify-between text-sm text-slate-600">
              <span>{isLogin ? "Don't have an account?" : 'Already have an account?'}</span>
              <button
                onClick={() => { setIsLogin(!isLogin); setError('') }}
                className="text-blue-600 font-semibold hover:underline"
              >
                {isLogin ? 'Register' : 'Login'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}