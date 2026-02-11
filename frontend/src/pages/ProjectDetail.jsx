import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import demoApi from '../utils/demoApi'
import AccountCard from '../components/AccountCard'
import IncidentCard from '../components/IncidentCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend } from 'recharts'
import { Activity, AlertTriangle, CheckCircle2, Sparkles } from 'lucide-react'

const COLORS = { P0: '#ef4444', P1: '#f59e0b', P2: '#3b82f6', P3: '#6b7280' }

function classNames(...xs) { return xs.filter(Boolean).join(' ') }

function Card({ title, value, icon }) {
  return (
    <div className="rounded-2xl border bg-slate-900/70 ring-1 ring-slate-800 p-4">
      <div className="flex items-center justify-between">
        <div><div className="text-xs text-slate-300">{title}</div><div className="text-2xl font-bold text-white mt-1">{value}</div></div>
        <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-200">{icon}</div>
      </div>
    </div>
  )
}

function Stat({ title, value }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3">
      <div className="text-xs text-slate-300">{title}</div>
      <div className="text-xl font-bold text-white mt-1">{value}</div>
    </div>
  )
}

function fmt(x) { return x === null || x === undefined || Number.isNaN(Number(x)) ? '-' : Number(x).toFixed(3) }

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
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [incidentEvents, setIncidentEvents] = useState([])
  const [incidentEventsTotal, setIncidentEventsTotal] = useState(0)
  const [incidentEventsLoading, setIncidentEventsLoading] = useState(false)
  const [incidentEventsMeta, setIncidentEventsMeta] = useState(null)
  const [incidentEventsOffset, setIncidentEventsOffset] = useState(0)
  const incidentEventsLimit = 20
  const [assistantMessages, setAssistantMessages] = useState([
    { role: 'assistant', content: 'Ask me anything about this incident.' }
  ])
  const [assistantSuggestions, setAssistantSuggestions] = useState([])
  const [assistantInput, setAssistantInput] = useState('')
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [selectedEventIndexes, setSelectedEventIndexes] = useState(() => new Set())

  // Compute derived metrics
  const core = demoOverview?.metrics || {}
  const totalPoints = Number(core.num_points || 0)
  const noisePoints = Number(core.num_noise || 0)
  const clusteredPoints = Math.max(0, totalPoints - noisePoints)

  const noiseBreakdown = useMemo(() => [
    { name: 'Clustered', value: clusteredPoints },
    { name: 'Noise', value: noisePoints },
  ].filter(x => x.value > 0), [clusteredPoints, noisePoints])

  const severityPie = useMemo(() => {
    const sc = demoOverview?.severity_counts || {}
    return Object.entries(sc).map(([k, v]) => ({ name: k, value: Number(v) }))
  }, [demoOverview])

  const topBars = useMemo(() => (clusters || []).slice(0, 10).map(c => ({
    name: `C${c.cluster_id}`,
    size: c.size,
    severity: c.severity,
  })), [clusters])

  const severityTrend = useMemo(() => {
    const byHour = {}
    for (let h = 0; h < 24; h += 1) byHour[h] = { hour: h, P0: 0, P1: 0, P2: 0, P3: 0 }
    for (const inc of demoIncidents || []) {
      const ts = inc?.start_time || inc?.startTime || inc?.timestamp || inc?.time
      if (!ts) continue
      const dt = new Date(ts)
      if (Number.isNaN(dt.getTime())) continue
      const h = dt.getHours()
      const sev = inc?.severity || 'P3'
      const w = Number(inc?.event_count || 1)
      if (byHour[h][sev] === undefined) byHour[h][sev] = 0
      byHour[h][sev] += w
    }
    return Object.values(byHour)
  }, [demoIncidents])

  const hasSeverityTrend = useMemo(
    () => severityTrend.some((h) => h.P0 + h.P1 + h.P2 + h.P3 > 0),
    [severityTrend]
  )

  const topIncidentTypes = useMemo(() => {
    const counts = {}
    for (const inc of demoIncidents || []) {
      const k = inc?.incident_type || 'unknown'
      counts[k] = (counts[k] || 0) + Number(inc?.event_count || 1)
    }
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6)
  }, [demoIncidents])

  const opsImpact = useMemo(() => {
    const totalEvents = (demoIncidents || []).reduce((acc, x) => acc + Number(x?.event_count || 0), 0)
    const p0Incidents = (demoIncidents || []).filter(x => x?.severity === 'P0').length
    const activeIncidents = (demoIncidents || []).length
    const estimatedMttdMin = activeIncidents > 0 ? Math.max(3, Math.round((p0Incidents * 8 + 20) / activeIncidents)) : 0
    return { totalEvents, p0Incidents, activeIncidents, estimatedMttdMin }
  }, [demoIncidents])

  const derivedErrorTypes = useMemo(() => {
    if ((errorTypes || []).length > 0) return errorTypes
    const counts = {}
    for (const inc of demoIncidents || []) {
      const k = inc?.incident_type || 'unknown'
      counts[k] = (counts[k] || 0) + Number(inc?.event_count || 1)
    }
    return Object.entries(counts)
      .map(([error_type, count]) => ({ error_type, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)
  }, [errorTypes, demoIncidents])

  const openIncident = (inc) => {
    setSelectedIncident(inc)
    setSolution(null)
    setIncidentEvents([])
    setIncidentEventsTotal(0)
    setIncidentEventsMeta(null)
    setIncidentEventsOffset(0)
    setAssistantMessages([{ role: 'assistant', content: 'Ask me anything about this incident.' }])
    setAssistantSuggestions([])
    setAssistantInput('')
    setSelectedEventIndexes(new Set())
    const id = inc?.incident_id || inc?.id
    if (!id) return
    setIncidentEventsLoading(true)
    demoApi
      .get(`/incident_events?incident_id=${encodeURIComponent(id)}&source=${encodeURIComponent(demoSource)}&limit=${incidentEventsLimit}&offset=0`)
      .then(({ data }) => {
        setIncidentEvents(Array.isArray(data?.events) ? data.events : [])
        setIncidentEventsTotal(Number(data?.total || 0))
        setIncidentEventsMeta(data || null)
      })
      .catch((err) => {
        console.error(err)
      })
      .finally(() => {
        setIncidentEventsLoading(false)
      })
  }

  const closeIncident = () => {
    setSelectedIncident(null)
    setSolution(null)
    setIncidentEvents([])
    setIncidentEventsTotal(0)
    setIncidentEventsMeta(null)
    setIncidentEventsOffset(0)
    setAssistantMessages([{ role: 'assistant', content: 'Ask me anything about this incident.' }])
    setAssistantSuggestions([])
    setAssistantInput('')
    setSelectedEventIndexes(new Set())
  }

  const fetchIncidentEventsPage = (nextOffset) => {
    const id = selectedIncident?.incident_id || selectedIncident?.id
    if (!id) return
    setIncidentEventsLoading(true)
    demoApi
      .get(`/incident_events?incident_id=${encodeURIComponent(id)}&source=${encodeURIComponent(demoSource)}&limit=${incidentEventsLimit}&offset=${Math.max(0, nextOffset)}`)
      .then(({ data }) => {
        setIncidentEvents(Array.isArray(data?.events) ? data.events : [])
        setIncidentEventsTotal(Number(data?.total || 0))
        setIncidentEventsMeta(data || null)
        setIncidentEventsOffset(Math.max(0, nextOffset))
      })
      .catch((err) => {
        console.error(err)
      })
      .finally(() => {
        setIncidentEventsLoading(false)
      })
  }

  const formatEventLine = (evt) => {
    if (!evt || typeof evt !== 'object') return String(evt ?? '')
    return evt.text || evt.message || evt.summary || JSON.stringify(evt)
  }

  const toggleEventSelected = (index) => {
    setSelectedEventIndexes((prev) => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }

  const clearSelectedEvents = () => setSelectedEventIndexes(new Set())

  const selectAllEvents = () => {
    setSelectedEventIndexes(new Set(incidentEvents.map((_, i) => i)))
  }

  const copySelectedEvents = async () => {
    const lines = incidentEvents
      .map((e, i) => (selectedEventIndexes.has(i) ? formatEventLine(e) : null))
      .filter(Boolean)
    if (lines.length === 0) return
    try {
      await navigator.clipboard.writeText(lines.join('\n'))
    } catch (err) {
      console.error(err)
    }
  }

  const sendAssistantMessage = async (text) => {
    const question = text?.trim()
    if (!question || assistantLoading) return
    const id = selectedIncident?.incident_id || selectedIncident?.id
    if (!id) return
    setAssistantLoading(true)
    setAssistantMessages((prev) => [...prev, { role: 'user', content: question }])
    setAssistantInput('')
    try {
      const { data } = await demoApi.post('/incident_assistant', {
        incident_id: id,
        question,
        source: demoSource,
      })
      if (data?.answer) {
        setAssistantMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
      }
      setAssistantSuggestions(Array.isArray(data?.suggestions) ? data.suggestions : [])
    } catch (err) {
      console.error(err)
      setAssistantMessages((prev) => [...prev, { role: 'assistant', content: 'Unable to fetch a response right now.' }])
    } finally {
      setAssistantLoading(false)
    }
  }

  const fetchDemoData = async () => {
    setDemoLoading(true)
    setDemoError('')
    try {
      const results = await Promise.allSettled([
        demoApi.get(`/clusters?source=${encodeURIComponent(demoSource)}&top_n=15`),
        demoApi.get(`/error_types?source=${encodeURIComponent(demoSource)}&top_n=8`),
        demoApi.get(`/log_samples?source=${encodeURIComponent(demoSource)}&limit=5`)
      ])
      const pickData = (res, fallback) => (res.status === 'fulfilled' ? res.value.data : fallback)
      const clustersData = pickData(results[0], { clusters: [] })
      const errorTypesData = pickData(results[1], { items: [] })
      const samplesData = pickData(results[2], { samples: [] })
      const anyOk = results.some(r => r.status === 'fulfilled')
      if (!anyOk) throw new Error('all requests failed')
      setClusters(clustersData?.clusters || [])
      setErrorTypes(errorTypesData?.items || [])
      setLogSamples(samplesData?.samples || [])
      if (results.some(r => r.status === 'rejected')) {
        setDemoError('Some demo data could not be loaded. Showing partial results.')
      }
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
        demoApi.get(`/uptime?source=${encodeURIComponent(demoSource)}`)
      ])
      setDemoStatus(statusRes.data || null)
      setDemoOverview(overviewRes.data || null)
      setDemoSources(sourcesRes.data?.sources || sourcesRes.data || [])
      const incidentsPayload = incidentsRes.data?.incidents ?? incidentsRes.data?.items ?? incidentsRes.data ?? []
      const normalizeSeverity = (s) => {
        if (!s) return 'P3'
        const key = String(s).toUpperCase()
        if (key === 'P0' || key === 'P1' || key === 'P2' || key === 'P3') return key
        if (key === 'CRITICAL') return 'P0'
        if (key === 'HIGH') return 'P1'
        if (key === 'MEDIUM') return 'P2'
        if (key === 'LOW') return 'P3'
        return 'P3'
      }
      const normalizedIncidents = Array.isArray(incidentsPayload)
        ? incidentsPayload.map((inc) => ({ ...inc, severity: normalizeSeverity(inc?.severity) }))
        : []
      setDemoIncidents(normalizedIncidents)
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
    <div className="min-h-screen bg-slate-950 text-white relative">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(16,185,129,0.16),_transparent_40%)]" />
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <button onClick={() => navigate('/')} className="text-blue-200 hover:underline mb-6 text-sm font-medium">
          ← Back to Projects
        </button>

        <div className="mb-8">
          <div className="flex items-start justify-between gap-4 mb-6">
            <div>
              <div className="inline-flex items-center gap-2 text-sm text-slate-300">
                <Sparkles className="w-4 h-4" />
                <span>MOZAIC Multi-Source Incident Intelligence</span>
              </div>
              <h1 className="text-3xl font-bold mt-2">{project.name}</h1>
              <p className="text-slate-300 mt-2">{project.description || 'Unified observability across Grafana, Kubernetes, CloudWatch, and Sentry with clustering and remediation guidance.'}</p>

              <div className="mt-4 inline-flex rounded-xl border border-slate-700 bg-slate-900/70 p-1">
                {['grafana','k8s','cloudwatch','sentry'].map(s => (
                  <button
                    key={s}
                    onClick={() => setDemoSource(s)}
                    className={classNames(
                      'px-3 py-1.5 text-sm rounded-lg',
                      demoSource === s ? 'bg-white text-slate-900 font-semibold' : 'text-slate-300 hover:text-white'
                    )}
                  >
                    {s === 'grafana' ? 'Grafana' : s === 'k8s' ? 'Kubernetes' : s === 'cloudwatch' ? 'CloudWatch' : 'Sentry'}
                  </button>
                ))}
              </div>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3">
              <div className="text-xs text-slate-400">API</div>
              <div className="font-mono text-sm text-slate-200">http://localhost:8000</div>
            </div>
          </div>

          {demoError ? (
            <div className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-amber-200 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 mt-0.5" />
              <div>
                <div className="font-semibold">Service not running</div>
                <div className="text-sm mt-1">{demoError}</div>
              </div>
            </div>
          ) : null}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card title="Points" value={core.num_points ?? '-'} icon={<Activity className="w-5 h-5" />} />
            <Card title="Clusters" value={core.num_clusters ?? '-'} icon={<CheckCircle2 className="w-5 h-5" />} />
            <Card title="Noise" value={core.num_noise ?? '-'} icon={<AlertTriangle className="w-5 h-5" />} />
            <Card title="Silhouette" value={fmt(core.silhouette_score)} icon={<Activity className="w-5 h-5" />} />
          </div>
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

        {/* Comprehensive Analytics Dashboard */}
        <div className="mt-12 space-y-8">
          {/* Operational Impact */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Operational Impact</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Stat title="Active Incidents" value={opsImpact.activeIncidents} />
              <Stat title="P0 Incidents" value={opsImpact.p0Incidents} />
              <Stat title="Total Events" value={opsImpact.totalEvents} />
              <Stat title="Est. MTTD (min)" value={opsImpact.estimatedMttdMin} />
            </div>
          </div>

          {/* Analytics Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Clusters Bar Chart */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Top Clusters by Size</h3>
              {topBars.length === 0 ? (
                <div className="h-64 flex items-center text-slate-300">No cluster data available</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topBars}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Bar dataKey="size" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Severity Distribution Pie */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
              {severityPie.length === 0 ? (
                <div className="h-64 flex items-center text-slate-300">No severity data available</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={severityPie} dataKey="value" cx="50%" cy="50%" outerRadius={80} label>
                      {severityPie.map(x => <Cell key={x.name} fill={COLORS[x.name] || '#6b7280'} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Noise Breakdown Pie */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Cluster vs Noise Breakdown</h3>
              {noiseBreakdown.length === 0 ? (
                <div className="h-64 flex items-center text-slate-300">No breakdown data</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={noiseBreakdown} dataKey="value" cx="50%" cy="50%" outerRadius={80} label>
                      <Cell fill="#3b82f6" />
                      <Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Error Types Bar */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Complete Checks (Error Types)</h3>
              {derivedErrorTypes.length === 0 ? (
                <div className="h-64 flex items-center text-slate-300">No error type data</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={derivedErrorTypes.slice(0, 8)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="error_type" stroke="#94a3b8" angle={-45} textAnchor="end" height={100} />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Bar dataKey="count" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Severity Trend Line */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Severity Trend by Hour</h3>
              {!hasSeverityTrend ? (
                <div className="h-64 flex items-center text-slate-300">No trend data</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={severityTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="hour" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Legend />
                    <Line type="monotone" dataKey="P0" stroke="#ef4444" />
                    <Line type="monotone" dataKey="P1" stroke="#f59e0b" />
                    <Line type="monotone" dataKey="P2" stroke="#3b82f6" />
                    <Line type="monotone" dataKey="P3" stroke="#6b7280" />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Top Incident Types */}
            <div className="bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Top Incident Types</h3>
              {topIncidentTypes.length === 0 ? (
                <div className="h-64 flex items-center text-slate-300">No incident type data</div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topIncidentTypes} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={120} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Bar dataKey="count" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Active Incidents Section */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Active Incidents</h2>
            {demoIncidents.length === 0 ? (
              <div className="text-center py-10 text-slate-300 bg-slate-900/70 rounded-3xl ring-1 ring-slate-800">
                No incidents
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {demoIncidents.slice(0, 12).map((inc, i) => (
                  <button
                    key={inc.id || i}
                    onClick={() => openIncident(inc)}
                    className="text-left bg-slate-900/70 rounded-2xl ring-1 ring-slate-800 p-4 hover:ring-slate-600 hover:bg-slate-800/70 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-white text-sm">{inc.title || inc.name || 'Incident'}</div>
                        <div className="text-xs text-slate-400 mt-1">{inc.incident_type || 'unknown'}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{inc.event_count || 1} events</div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-semibold ${inc.severity === 'P0' ? 'bg-red-500/20 text-red-200' : inc.severity === 'P1' ? 'bg-amber-500/20 text-amber-200' : inc.severity === 'P2' ? 'bg-blue-500/20 text-blue-200' : 'bg-slate-700/20 text-slate-300'}`}>
                        {inc.severity}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Cluster Analysis Section */}
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold">Cluster Analysis</h2>
              <p className="text-sm text-slate-300">Detailed cluster information with resolution steps.</p>
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

          {demoLoading ? (
            <div className="text-slate-300">Loading cluster analysis...</div>
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
                                className="bg-white text-slate-900 px-3 py-1.5 rounded-xl font-semibold hover:bg-slate-200 text-xs"
                              >
                                Resolve
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
                <h3 className="text-lg font-semibold mb-3">Evidence & Resolution</h3>

                <div>
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Error Types Detected</h4>
                  {derivedErrorTypes.length === 0 ? (
                    <div className="text-slate-300 text-xs">No error types found.</div>
                  ) : (
                    <ul className="space-y-1 text-xs">
                      {derivedErrorTypes.slice(0, 5).map((e) => (
                        <li key={e.error_type} className="flex items-center justify-between text-slate-300">
                          <span>{e.error_type}</span>
                          <span className="text-slate-500">{e.count}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="mt-4 border-t border-slate-800 pt-4">
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Log Samples</h4>
                  {logSamples.length === 0 ? (
                    <div className="text-slate-300 text-xs">No samples loaded.</div>
                  ) : (
                    <div className="space-y-1">
                      {logSamples.slice(0, 2).map((s, i) => (
                        <pre key={i} className="text-xs bg-slate-950 text-slate-100 rounded p-2 overflow-auto max-h-20">{s}</pre>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-4 border-t border-slate-800 pt-4">
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Recommended Actions</h4>
                  {solutionLoading ? (
                    <div className="text-sm text-slate-300">Loading...</div>
                  ) : solution ? (
                    <ol className="list-decimal pl-4 text-xs text-slate-300 space-y-1">
                      {solution.recommended_actions?.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ol>
                  ) : (
                    <div className="text-xs text-slate-300">Select a cluster to view actions.</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Incident Detail Modal */}
        {selectedIncident && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm pointer-events-auto">
            <div className="bg-slate-900/95 ring-1 ring-slate-800 rounded-3xl max-w-5xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
              <div className="sticky top-0 bg-slate-900/95 border-b border-slate-800 p-6 flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold">{selectedIncident.title || 'Incident Details'}</h3>
                  <div className="text-xs text-slate-400 mt-1">{selectedIncident.incident_id || selectedIncident.id}</div>
                </div>
                <button onClick={closeIncident} className="text-slate-400 hover:text-white">✕</button>
              </div>
              <div className="p-6 space-y-5 overflow-auto max-h-[calc(80vh-88px)]">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="text-slate-400">Type</div>
                    <div className="text-white font-semibold break-words">{selectedIncident.incident_type || 'Unknown'}</div>
                  </div>
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="text-slate-400">Severity</div>
                    <div className={`font-semibold ${selectedIncident.severity === 'P0' ? 'text-red-400' : selectedIncident.severity === 'P1' ? 'text-amber-400' : selectedIncident.severity === 'P2' ? 'text-blue-400' : 'text-slate-300'}`}>
                      {selectedIncident.severity}
                    </div>
                  </div>
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="text-slate-400">Events</div>
                    <div className="text-white font-semibold">{selectedIncident.event_count ?? 0}</div>
                  </div>
                  {/* <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="text-slate-400">Source</div>
                    <div className="text-white font-semibold">
                      {selectedIncident.source || selectedIncident.service || 'Unknown'}
                    </div>
                    {incidentEventsMeta?.fallback && incidentEventsMeta?.log_source && (
                      <div className="text-xs text-slate-400 mt-1">events from {incidentEventsMeta.log_source}</div>
                    )}
                  </div> */}
                </div>
                {selectedIncident.description && (
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="text-slate-400 text-sm mb-1">Description</div>
                    <p className="text-slate-200 text-sm">{selectedIncident.description}</p>
                  </div>
                )}
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-slate-200 text-sm font-semibold">Events</div>
                    <div className="flex items-center gap-3">
                      <div className="text-xs text-slate-400">
                        Showing {incidentEvents.length} of {incidentEventsTotal}
                      </div>
                      {incidentEventsTotal > incidentEventsLimit && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => fetchIncidentEventsPage(incidentEventsOffset - incidentEventsLimit)}
                            disabled={incidentEventsOffset <= 0 || incidentEventsLoading}
                            className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
                          >
                            Prev
                          </button>
                          <div className="text-xs text-slate-400">
                            {Math.floor(incidentEventsOffset / incidentEventsLimit) + 1}/{Math.max(1, Math.ceil(incidentEventsTotal / incidentEventsLimit))}
                          </div>
                          <button
                            onClick={() => fetchIncidentEventsPage(incidentEventsOffset + incidentEventsLimit)}
                            disabled={incidentEventsOffset + incidentEventsLimit >= incidentEventsTotal || incidentEventsLoading}
                            className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
                          >
                            Next
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="mb-3 flex items-center gap-2">
                    <button
                      onClick={selectAllEvents}
                      disabled={incidentEvents.length === 0}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
                    >
                      Select all
                    </button>
                    <button
                      onClick={clearSelectedEvents}
                      disabled={selectedEventIndexes.size === 0}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
                    >
                      Clear
                    </button>
                    <button
                      onClick={copySelectedEvents}
                      disabled={selectedEventIndexes.size === 0}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
                    >
                      Copy selected ({selectedEventIndexes.size})
                    </button>
                  </div>
                  {incidentEventsLoading ? (
                    <div className="text-slate-300 text-sm">Loading events...</div>
                  ) : incidentEvents.length === 0 ? (
                    <div className="text-slate-300 text-sm">No events found for this incident.</div>
                  ) : (
                    <div className="space-y-2">
                      {incidentEvents.map((e, i) => (
                        <button
                          key={i}
                          onClick={() => toggleEventSelected(i)}
                          className={classNames(
                            'w-full text-left text-xs rounded-xl p-3 whitespace-pre-wrap break-words border',
                            selectedEventIndexes.has(i)
                              ? 'bg-blue-500/10 text-blue-100 border-blue-500/30'
                              : 'bg-slate-900 text-slate-100 border-slate-800 hover:border-slate-700'
                          )}
                        >
                          {formatEventLine(e)}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-950/80 to-slate-900/60 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-slate-200 text-sm font-semibold">Incident Copilot</div>
                    <div className="text-xs text-slate-400">AI assistant</div>
                  </div>

                  <div className="max-h-48 overflow-auto space-y-2 pr-1">
                    {assistantMessages.map((m, i) => (
                      <div
                        key={i}
                        className={classNames(
                          'rounded-xl px-3 py-2 text-sm',
                          m.role === 'user'
                            ? 'bg-blue-500/10 text-blue-100 ring-1 ring-blue-500/20 ml-8'
                            : 'bg-slate-900/70 text-slate-100 ring-1 ring-slate-800 mr-8'
                        )}
                      >
                        {m.content}
                      </div>
                    ))}
                    {assistantLoading && (
                      <div className="rounded-xl px-3 py-2 text-sm bg-slate-900/70 text-slate-300 ring-1 ring-slate-800 mr-8">
                        Thinking...
                      </div>
                    )}
                  </div>

                  {assistantSuggestions.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {assistantSuggestions.slice(0, 4).map((s, i) => (
                        <button
                          key={i}
                          onClick={() => sendAssistantMessage(s)}
                          className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}

                  <div className="mt-3 flex items-center gap-2">
                    <input
                      value={assistantInput}
                      onChange={(e) => setAssistantInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') sendAssistantMessage(assistantInput)
                      }}
                      placeholder="Ask about root cause, impact, timeline..."
                      className="flex-1 px-3 py-2 rounded-xl bg-slate-950 text-slate-100 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                    />
                    <button
                      onClick={() => sendAssistantMessage(assistantInput)}
                      disabled={assistantLoading || !assistantInput.trim()}
                      className="px-4 py-2 rounded-xl bg-white text-slate-900 font-semibold disabled:opacity-50"
                    >
                      Ask
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}