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
    <div className="max-w-2xl mx-auto px-4 py-8">
      <button onClick={() => navigate(`/project/${id}`)} className="text-blue-600 hover:underline mb-4">
        ← Back to Project
      </button>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-6">Connect Account</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Service Type</label>
            <select
              value={serviceType}
              onChange={(e) => { setServiceType(e.target.value); setCredentials({}) }}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              <label className="block text-sm font-medium mb-2">{field.label}</label>
              {field.type === 'textarea' ? (
                <textarea
                  value={credentials[field.name] || ''}
                  onChange={(e) => setCredentials({ ...credentials, [field.name]: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="6"
                  placeholder={field.placeholder}
                  required
                />
              ) : (
                <input
                  type={field.type}
                  value={credentials[field.name] || ''}
                  onChange={(e) => setCredentials({ ...credentials, [field.name]: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={field.placeholder}
                  required
                />
              )}
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Connecting...' : 'Connect'}
          </button>
        </form>
      </div>
    </div>
  )
}