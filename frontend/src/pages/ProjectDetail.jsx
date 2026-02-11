import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import demoApi from '../utils/demoApi'
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
  const [demoSource, setDemoSource] = useState('grafana')
  const [demoLoading, setDemoLoading] = useState(true)
  const [demoError, setDemoError] = useState('')
  const [clusters, setClusters] = useState([])
  const [errorTypes, setErrorTypes] = useState([])
  const [logSamples, setLogSamples] = useState([])
  const [solution, setSolution] = useState(null)
  const [solutionLoading, setSolutionLoading] = useState(false)

  const fetchDemoData = async () => {
    setDemoLoading(true)
    setDemoError('')
    try {
      const [clustersRes, errorTypesRes, samplesRes] = await Promise.all([
        demoApi.get(`/clusters?source=${encodeURIComponent(demoSource)}&top_n=15`),
        demoApi.get(`/error_types?source=${encodeURIComponent(demoSource)}&top_n=8`),
        demoApi.get(`/log_samples?source=${encodeURIComponent(demoSource)}&limit=5`)
      ])
      setClusters(clustersRes.data?.clusters || [])
      setErrorTypes(errorTypesRes.data?.items || [])
      setLogSamples(samplesRes.data?.samples || [])
    } catch (err) {
      console.error(err)
      setDemoError('Demo API not reachable. Please start the backend demo routes.')
      setClusters([])
      setErrorTypes([])
      setLogSamples([])
    } finally {
      setDemoLoading(false)
    }
  }

  const handleGetSolution = async (cluster) => {
    setSolution(null)
    setSolutionLoading(true)
    try {
      const { data } = await demoApi.post('/solution', {
        cluster_id: cluster.cluster_id,
        error_type: cluster.error_type,
        severity: cluster.severity,
      })
      setSolution(data)
    } catch (err) {
      console.error(err)
      setDemoError('Failed to fetch resolution from demo API.')
    } finally {
      setSolutionLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [id])

  useEffect(() => {
    fetchDemoData()
  }, [demoSource])

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

      <div className="mt-10">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
          <div>
            <h2 className="text-2xl font-bold">Cluster Analysis (Demo)</h2>
            <p className="text-sm text-gray-600">Use demo routes to see clusters, root cause labels, checks, and resolution steps.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Source</span>
            <select
              value={demoSource}
              onChange={(e) => setDemoSource(e.target.value)}
              className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="grafana">Grafana</option>
              <option value="k8s">Kubernetes</option>
              <option value="cloudwatch">CloudWatch</option>
              <option value="sentry">Sentry</option>
            </select>
          </div>
        </div>

        {demoError && (
          <div className="mb-4 p-3 bg-amber-50 text-amber-900 rounded border border-amber-200">{demoError}</div>
        )}

        {demoLoading ? (
          <div className="text-gray-600">Loading demo analysis...</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Clusters (size, severity, cause)</h3>
              {clusters.length === 0 ? (
                <div className="text-gray-500">No clusters available for this source.</div>
              ) : (
                <div className="overflow-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 border-b">
                        <th className="py-2 pr-4">Cluster</th>
                        <th className="py-2 pr-4">Size</th>
                        <th className="py-2 pr-4">Severity</th>
                        <th className="py-2 pr-4">Actual Cause</th>
                        <th className="py-2 pr-4">Resolution</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clusters.map((c) => (
                        <tr key={c.cluster_id} className="border-b last:border-b-0">
                          <td className="py-2 pr-4 font-medium">C{c.cluster_id}</td>
                          <td className="py-2 pr-4">{c.size}</td>
                          <td className="py-2 pr-4">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${c.severity === 'P0' ? 'bg-red-50 text-red-700' : c.severity === 'P1' ? 'bg-amber-50 text-amber-700' : 'bg-blue-50 text-blue-700'}`}>
                              {c.severity}
                            </span>
                          </td>
                          <td className="py-2 pr-4 text-gray-700">{c.error_type}</td>
                          <td className="py-2 pr-4">
                            <button
                              onClick={() => handleGetSolution(c)}
                              className="bg-gray-900 text-white px-3 py-1.5 rounded-md hover:bg-gray-800"
                            >
                              Get resolution
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-3">Complete Checks</h3>
              {errorTypes.length === 0 ? (
                <div className="text-gray-500 text-sm">No error types available.</div>
              ) : (
                <ul className="space-y-2 text-sm">
                  {errorTypes.map((e) => (
                    <li key={e.error_type} className="flex items-center justify-between">
                      <span className="text-gray-700">{e.error_type}</span>
                      <span className="text-gray-500">{e.count}</span>
                    </li>
                  ))}
                </ul>
              )}

              <div className="mt-5">
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Evidence (log samples)</h4>
                {logSamples.length === 0 ? (
                  <div className="text-gray-500 text-sm">No samples loaded.</div>
                ) : (
                  <div className="space-y-2">
                    {logSamples.slice(0, 5).map((s, i) => (
                      <pre key={i} className="text-xs bg-gray-900 text-gray-100 rounded-md p-3 overflow-auto max-h-32">{s}</pre>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-5">
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Resolution Output</h4>
                {solutionLoading ? (
                  <div className="text-sm text-gray-600">Loading resolution...</div>
                ) : solution ? (
                  <div>
                    <div className="text-xs text-gray-500 mb-2">
                      Cluster {solution.cluster_id} · {solution.severity} · {solution.error_type}
                    </div>
                    <ol className="list-decimal pl-5 text-sm text-gray-800 space-y-1">
                      {solution.recommended_actions?.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ol>
                    <div className="text-xs text-gray-500 mt-2">{solution.note}</div>
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">Select a cluster to get resolution steps.</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}