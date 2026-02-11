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
  const [demoStatus, setDemoStatus] = useState(null)
  const [demoOverview, setDemoOverview] = useState(null)
  const [demoSources, setDemoSources] = useState([])
  const [demoIncidents, setDemoIncidents] = useState([])
  const [demoUptime, setDemoUptime] = useState(null)
  const [outputDir, setOutputDir] = useState('')
  const [outputSaving, setOutputSaving] = useState(false)
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

  const fetchDemoMeta = async () => {
    try {
      const [statusRes, overviewRes, sourcesRes, incidentsRes, uptimeRes] = await Promise.all([
        demoApi.get('/status'),
        demoApi.get('/overview'),
        demoApi.get('/sources'),
        demoApi.get('/incidents'),
        demoApi.get('/uptime')
      ])
      setDemoStatus(statusRes.data || null)
      setDemoOverview(overviewRes.data || null)
      setDemoSources(sourcesRes.data?.sources || sourcesRes.data || [])
      const incidentsPayload = incidentsRes.data?.incidents ?? incidentsRes.data?.items ?? incidentsRes.data ?? []
      setDemoIncidents(Array.isArray(incidentsPayload) ? incidentsPayload : [])
      setDemoUptime(uptimeRes.data || null)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSetOutputDir = async () => {
    if (!outputDir.trim()) return
    setOutputSaving(true)
    try {
      await demoApi.post('/set_output_dir', { output_dir: outputDir.trim() })
      await fetchDemoMeta()
    } catch (err) {
      console.error(err)
      setDemoError('Failed to set output directory.')
    } finally {
      setOutputSaving(false)
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

  useEffect(() => {
    fetchDemoMeta()
  }, [])

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


  if (loading) return <div className="flex justify-center items-center h-screen bg-slate-950 text-slate-300">Loading...</div>

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(16,185,129,0.16),_transparent_40%)]" />
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <button onClick={() => navigate('/')} className="text-blue-200 hover:underline mb-6 text-sm font-medium">
          ← Back to Projects
        </button>

        <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6 mb-8">
          <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-3 py-1 text-xs font-semibold ring-1 ring-blue-500/30">
            Project Overview
          </div>
          <h1 className="text-3xl font-bold mt-4">{project.name}</h1>
          <p className="text-slate-300 mt-2">{project.description || 'No description'}</p>
        </div>

        <div className="mb-10">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold">Connected Accounts</h2>
              <p className="text-sm text-slate-300">Manage linked sources for this project.</p>
            </div>
            <button
              onClick={() => navigate(`/project/${id}/connect`)}
              className="bg-white text-slate-900 px-4 py-2.5 rounded-xl font-semibold hover:bg-slate-200 transition"
            >
              Connect Account
            </button>
          </div>
          {accounts.length === 0 ? (
            <div className="text-center py-10 text-slate-300 bg-slate-900/70 rounded-3xl ring-1 ring-slate-800">
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
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold">Incidents</h2>
              <p className="text-sm text-slate-300">Latest detections across connected sources.</p>
            </div>
            <button
              onClick={handleManualFetch}
              disabled={fetching}
              className="bg-emerald-400 text-slate-900 px-4 py-2.5 rounded-xl font-semibold hover:bg-emerald-300 disabled:opacity-50"
            >
              {fetching ? 'Fetching...' : 'Fetch Now'}
            </button>
          </div>
          {incidents.length === 0 ? (
            <div className="text-center py-10 text-slate-300 bg-slate-900/70 rounded-3xl ring-1 ring-slate-800">
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

        <div className="mt-12">
          <div className="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">Demo Status</h3>
                  <p className="text-sm text-slate-300">Runtime health and uptime snapshot.</p>
                </div>
                <button
                  onClick={fetchDemoMeta}
                  className="text-xs font-semibold text-blue-200 hover:text-blue-100"
                >
                  Refresh
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-slate-950/70 rounded-2xl p-4 ring-1 ring-slate-800">
                  <div className="text-slate-400">Status</div>
                  <div className="text-white font-semibold mt-1">{demoStatus?.status || demoStatus?.state || 'Unknown'}</div>
                </div>
                <div className="bg-slate-950/70 rounded-2xl p-4 ring-1 ring-slate-800">
                  <div className="text-slate-400">Uptime</div>
                  <div className="text-white font-semibold mt-1">{demoUptime?.uptime || demoUptime?.seconds || 'N/A'}</div>
                </div>
                <div className="bg-slate-950/70 rounded-2xl p-4 ring-1 ring-slate-800">
                  <div className="text-slate-400">Output Dir</div>
                  <div className="text-white font-semibold mt-1 truncate">{demoStatus?.output_dir || demoOverview?.output_dir || 'Not set'}</div>
                </div>
              </div>

              <div className="mt-5">
                <label className="block text-sm font-medium text-slate-300 mb-2">Set Output Directory</label>
                <div className="flex flex-col md:flex-row gap-3">
                  <input
                    value={outputDir}
                    onChange={(e) => setOutputDir(e.target.value)}
                    placeholder="D:/data/mozaic/output"
                    className="flex-1 px-3 py-2.5 border border-slate-700 rounded-xl bg-slate-950 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                  />
                  <button
                    type="button"
                    onClick={handleSetOutputDir}
                    disabled={outputSaving}
                    className="bg-white text-slate-900 px-4 py-2.5 rounded-xl font-semibold hover:bg-slate-200 disabled:opacity-50"
                  >
                    {outputSaving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold">Overview</h3>
              <p className="text-sm text-slate-300 mb-4">Demo metrics and counts.</p>
              {demoOverview ? (
                <div className="space-y-2 text-sm">
                  {Object.entries(demoOverview).slice(0, 8).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-slate-300 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="text-slate-100 font-semibold">{String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-slate-300">No overview data.</div>
              )}
            </div>
          </div>

          <div className="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold">Sources</h3>
              <p className="text-sm text-slate-300 mb-4">Registered demo sources.</p>
              {demoSources.length === 0 ? (
                <div className="text-sm text-slate-300">No sources found.</div>
              ) : (
                <ul className="space-y-2 text-sm">
                  {demoSources.slice(0, 10).map((s, i) => {
                    const label = typeof s === 'string' ? s : (s.label || s.name || s.id || s.source || 'Unknown')
                    const meta = typeof s === 'string' ? '' : (s.count ?? s.total ?? (s.has_logs !== undefined ? (s.has_logs ? 'logs' : 'no logs') : ''))
                    const key = typeof s === 'string' ? s : (s.id || s.name || s.label || i)
                    return (
                      <li key={`${key}-${i}`} className="flex items-center justify-between">
                        <span className="text-slate-200">{label}</span>
                        <span className="text-slate-400">{meta}</span>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>

            <div className="lg:col-span-2 bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold">Demo Incidents</h3>
              <p className="text-sm text-slate-300 mb-4">Latest demo incidents stream.</p>
              {demoIncidents.length === 0 ? (
                <div className="text-sm text-slate-300">No incidents available.</div>
              ) : (
                <div className="space-y-3">
                  {demoIncidents.slice(0, 6).map((item, i) => (
                    <div key={item.id || i} className="bg-slate-950/70 rounded-2xl p-4 ring-1 ring-slate-800">
                      <div className="flex items-center justify-between text-sm">
                        <div className="font-semibold text-slate-100">{item.title || item.name || 'Incident'}</div>
                        <div className="text-slate-400">{item.severity || item.level || 'N/A'}</div>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">{item.source || item.service || 'Unknown source'}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div>
              <h2 className="text-2xl font-bold">Cluster Analysis (Demo)</h2>
              <p className="text-sm text-slate-300">Use demo routes to see clusters, root cause labels, checks, and resolution steps.</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-300">Source</span>
              <select
                value={demoSource}
                onChange={(e) => setDemoSource(e.target.value)}
                className="px-3 py-2 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/40 bg-slate-950 text-white"
              >
                <option value="grafana">Grafana</option>
                <option value="k8s">Kubernetes</option>
                <option value="cloudwatch">CloudWatch</option>
                <option value="sentry">Sentry</option>
              </select>
            </div>
          </div>

          {demoError && (
            <div className="mb-4 p-3 bg-amber-500/10 text-amber-200 rounded-xl border border-amber-500/30 text-sm">{demoError}</div>
          )}

          {demoLoading ? (
            <div className="text-slate-300">Loading demo analysis...</div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
                <h3 className="text-lg font-semibold mb-4">Clusters (size, severity, cause)</h3>
                {clusters.length === 0 ? (
                  <div className="text-slate-300">No clusters available for this source.</div>
                ) : (
                  <div className="overflow-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-slate-400 border-b border-slate-800">
                          <th className="py-2 pr-4">Cluster</th>
                          <th className="py-2 pr-4">Size</th>
                          <th className="py-2 pr-4">Severity</th>
                          <th className="py-2 pr-4">Actual Cause</th>
                          <th className="py-2 pr-4">Resolution</th>
                        </tr>
                      </thead>
                      <tbody>
                        {clusters.map((c) => (
                          <tr key={c.cluster_id} className="border-b border-slate-800 last:border-b-0">
                            <td className="py-2 pr-4 font-medium">C{c.cluster_id}</td>
                            <td className="py-2 pr-4 text-slate-300">{c.size}</td>
                            <td className="py-2 pr-4">
                              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${c.severity === 'P0' ? 'bg-red-500/10 text-red-200 ring-1 ring-red-500/30' : c.severity === 'P1' ? 'bg-amber-500/10 text-amber-200 ring-1 ring-amber-500/30' : 'bg-blue-500/10 text-blue-200 ring-1 ring-blue-500/30'}`}>
                                {c.severity}
                              </span>
                            </td>
                            <td className="py-2 pr-4 text-slate-300">{c.error_type}</td>
                            <td className="py-2 pr-4">
                              <button
                                onClick={() => handleGetSolution(c)}
                                className="bg-white text-slate-900 px-3 py-1.5 rounded-xl font-semibold hover:bg-slate-200"
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

              <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
                <h3 className="text-lg font-semibold mb-3">Complete Checks</h3>
                {errorTypes.length === 0 ? (
                  <div className="text-slate-300 text-sm">No error types available.</div>
                ) : (
                  <ul className="space-y-2 text-sm">
                    {errorTypes.map((e) => (
                      <li key={e.error_type} className="flex items-center justify-between">
                        <span className="text-slate-200">{e.error_type}</span>
                        <span className="text-slate-400">{e.count}</span>
                      </li>
                    ))}
                  </ul>
                )}

                <div className="mt-5">
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Evidence (log samples)</h4>
                  {logSamples.length === 0 ? (
                    <div className="text-slate-300 text-sm">No samples loaded.</div>
                  ) : (
                    <div className="space-y-2">
                      {logSamples.slice(0, 5).map((s, i) => (
                        <pre key={i} className="text-xs bg-slate-950 text-slate-100 rounded-xl p-3 overflow-auto max-h-32">{s}</pre>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-5">
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Resolution Output</h4>
                  {solutionLoading ? (
                    <div className="text-sm text-slate-300">Loading resolution...</div>
                  ) : solution ? (
                    <div>
                      <div className="text-xs text-slate-400 mb-2">
                        Cluster {solution.cluster_id} · {solution.severity} · {solution.error_type}
                      </div>
                      <ol className="list-decimal pl-5 text-sm text-slate-200 space-y-1">
                        {solution.recommended_actions?.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ol>
                      <div className="text-xs text-slate-400 mt-2">{solution.note}</div>
                    </div>
                  ) : (
                    <div className="text-sm text-slate-300">Select a cluster to get resolution steps.</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}