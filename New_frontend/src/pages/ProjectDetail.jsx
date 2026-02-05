import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import AccountCard from '../components/AccountCard'
import IncidentCard from '../components/IncidentCard'

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [accounts, setAccounts] = useState([])
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)

  useEffect(() => {
    fetchData()
  }, [id])

  const fetchData = async () => {
    try {
      const [projectRes, accountsRes, incidentsRes] = await Promise.all([
        api.get(`/projects/${id}`),
        api.get(`/accounts/project/${id}`),
        api.get(`/incidents/project/${id}`)
      ])
      setProject(projectRes.data)
      setAccounts(accountsRes.data)
      setIncidents(incidentsRes.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleManualFetch = async () => {
    setFetching(true)
    try {
      await api.post(`/incidents/fetch/${id}`)
      fetchData()
    } catch (err) {
      console.error(err)
    } finally {
      setFetching(false)
    }
  }

  const handleDeleteAccount = async (accountId) => {
    if (!confirm('Delete this connection?')) return
    try {
      await api.delete(`/accounts/${accountId}`)
      fetchData()
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) return <div className="flex justify-center items-center h-screen">Loading...</div>

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <button onClick={() => navigate('/')} className="text-blue-600 hover:underline mb-4">
        ← Back to Projects
      </button>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h1 className="text-3xl font-bold mb-2">{project.name}</h1>
        <p className="text-gray-600">{project.description || 'No description'}</p>
      </div>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Connected Accounts</h2>
          <button
            onClick={() => navigate(`/project/${id}/connect`)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Connect Account
          </button>
        </div>
        {accounts.length === 0 ? (
          <div className="text-center py-8 text-gray-500 bg-white rounded-lg">
            No accounts connected yet
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {accounts.map(account => (
              <AccountCard
                key={account.id}
                account={account}
                onDelete={handleDeleteAccount}
              />
            ))}
          </div>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Incidents</h2>
          <button
            onClick={handleManualFetch}
            disabled={fetching}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {fetching ? 'Fetching...' : 'Fetch Now'}
          </button>
        </div>
        {incidents.length === 0 ? (
          <div className="text-center py-8 text-gray-500 bg-white rounded-lg">
            No incidents detected
          </div>
        ) : (
          <div className="space-y-4">
            {incidents.map(incident => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}