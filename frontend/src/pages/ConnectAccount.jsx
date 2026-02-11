import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'

export default function ConnectAccount() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [serviceType, setServiceType] = useState('kubernetes')
  const [credentials, setCredentials] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const serviceFields = {
    kubernetes: [{ name: 'kubeconfig', label: 'Kubeconfig (JSON)', type: 'textarea' }],
    docker: [{ name: 'base_url', label: 'Base URL', type: 'text', placeholder: 'unix://var/run/docker.sock' }],
    cloudwatch: [
      { name: 'aws_access_key_id', label: 'AWS Access Key ID', type: 'text' },
      { name: 'aws_secret_access_key', label: 'AWS Secret Key', type: 'password' },
      { name: 'region', label: 'Region', type: 'text', placeholder: 'us-east-1' }
    ],
    grafana: [
      { name: 'url', label: 'Grafana URL', type: 'text', placeholder: 'https://your-grafana.com' },
      { name: 'api_key', label: 'API Key', type: 'password' }
    ],
    sentry: [
      { name: 'auth_token', label: 'Auth Token', type: 'password' },
      { name: 'org_slug', label: 'Organization Slug', type: 'text' },
      { name: 'project_slug', label: 'Project Slug', type: 'text' }
    ]
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        project_id: id,
        service_type: serviceType,
        credentials: serviceType === 'kubernetes' 
          ? JSON.parse(credentials.kubeconfig || '{}')
          : credentials
      }
      await api.post('/accounts/', payload)
      navigate(`/project/${id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Connection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(99,102,241,0.16),_transparent_40%)]" />
      <div className="relative z-10 max-w-3xl mx-auto px-4 py-12">
        <button onClick={() => navigate(`/project/${id}`)} className="text-blue-200 hover:underline mb-6 text-sm font-medium">
          ← Back to Project
        </button>

        <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6 md:p-8">
          <div className="mb-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-3 py-1 text-xs font-semibold ring-1 ring-blue-500/30">
              Secure Connection
            </div>
            <h1 className="text-2xl font-bold mt-4">Connect Account</h1>
            <p className="text-sm text-slate-300 mt-1">Securely link a source to start collecting incidents.</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 text-red-200 rounded-xl ring-1 ring-red-500/30 text-sm">{error}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-300 mb-2">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => { setServiceType(e.target.value); setCredentials({}) }}
                className="w-full px-3 py-2.5 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/40 bg-slate-950 text-white"
              >
                <option value="kubernetes">Kubernetes</option>
                <option value="docker">Docker</option>
                <option value="cloudwatch">CloudWatch</option>
                <option value="grafana">Grafana</option>
                <option value="sentry">Sentry</option>
              </select>
            </div>

            {serviceFields[serviceType].map(field => (
              <div key={field.name} className="mb-4">
                <label className="block text-sm font-medium text-slate-300 mb-2">{field.label}</label>
                {field.type === 'textarea' ? (
                  <textarea
                    value={credentials[field.name] || ''}
                    onChange={(e) => setCredentials({ ...credentials, [field.name]: e.target.value })}
                    className="w-full px-3 py-2.5 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/40 bg-slate-950 text-white placeholder:text-slate-500"
                    rows="6"
                    placeholder={field.placeholder}
                    required
                  />
                ) : (
                  <input
                    type={field.type}
                    value={credentials[field.name] || ''}
                    onChange={(e) => setCredentials({ ...credentials, [field.name]: e.target.value })}
                    className="w-full px-3 py-2.5 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/40 bg-slate-950 text-white placeholder:text-slate-500"
                    placeholder={field.placeholder}
                    required
                  />
                )}
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-slate-900 py-3 rounded-xl font-semibold hover:bg-slate-200 transition disabled:opacity-50"
            >
              {loading ? 'Connecting...' : 'Connect'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}