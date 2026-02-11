import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts'
import { Activity, AlertTriangle, CheckCircle2, Sparkles } from 'lucide-react'

const demoApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/demo',
  headers: { 'Content-Type': 'application/json' },
})

const COLORS = {
  P0: '#ef4444',
  P1: '#f59e0b',
  P2: '#3b82f6',
  P3: '#6b7280',
}

function classNames(...xs) {
  return xs.filter(Boolean).join(' ')
}

export default function DemoDashboard() {
  const [overview, setOverview] = useState(null)
  const [clusters, setClusters] = useState([])
  const [errorTypes, setErrorTypes] = useState([])
  const [uptime, setUptime] = useState([])
  const [source, setSource] = useState('grafana')
  const [loading, setLoading] = useState(true)
  const [incidents, setIncidents] = useState([])
  const [logSamples, setLogSamples] = useState([])
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [solution, setSolution] = useState(null)
  const [solutionLoading, setSolutionLoading] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    let mounted = true
    async function run() {
      setLoading(true)
      setErr('')
      try {
        const results = await Promise.allSettled([
          demoApi.get(`/overview?source=${encodeURIComponent(source)}`),
          demoApi.get(`/clusters?source=${encodeURIComponent(source)}&top_n=15`),
          demoApi.get(`/error_types?source=${encodeURIComponent(source)}&top_n=8`),
          demoApi.get(`/uptime?source=${encodeURIComponent(source)}`),
          demoApi.get('/incidents'),
          demoApi.get(`/log_samples?source=${encodeURIComponent(source)}&limit=5`),
        ])
        const pickData = (res, fallback) => (res.status === 'fulfilled' ? res.value.data : fallback)
        const ovData = pickData(results[0], { metrics: {}, severity_counts: {} })
        const clData = pickData(results[1], { clusters: [] })
        const etData = pickData(results[2], { items: [] })
        const upData = pickData(results[3], { series: [] })
        const incData = pickData(results[4], { incidents: [] })
        const sampData = pickData(results[5], { samples: [] })
        const anyOk = results.some(r => r.status === 'fulfilled')
        if (!anyOk) {
          throw new Error('all requests failed')
        }
        if (!mounted) return
        setOverview(ovData)
        setClusters(clData?.clusters || [])
        setErrorTypes(etData?.items || [])
        setUptime(upData?.series || [])
        setIncidents(incData?.incidents || [])
        setLogSamples(sampData?.samples || [])
        if (results.some(r => r.status === 'rejected')) {
          setErr('Some demo data could not be loaded. Showing partial results.')
        }
      } catch (e) {
        console.error(e)
        setErr('API not reachable. Start backend API on :8000.')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    run()
    return () => {
      mounted = false
    }
  }, [source])

  const severityPie = useMemo(() => {
    const sc = overview?.severity_counts || {}
    return Object.entries(sc).map(([k, v]) => ({ name: k, value: Number(v) }))
  }, [overview])

  const topBars = useMemo(() => {
    return (clusters || []).slice(0, 10).map(c => ({
      name: `C${c.cluster_id}`,
      size: c.size,
      severity: c.severity,
    }))
  }, [clusters])

  const core = overview?.metrics || {}
  const totalPoints = Number(core.num_points || 0)
  const noisePoints = Number(core.num_noise || 0)
  const clusteredPoints = Math.max(0, totalPoints - noisePoints)

  const noiseBreakdown = useMemo(() => {
    if (totalPoints <= 0) return []
    return [
      { name: 'Clustered', value: clusteredPoints },
      { name: 'Noise', value: noisePoints },
    ]
  }, [clusteredPoints, noisePoints, totalPoints])

  const severityTrend = useMemo(() => {
    const byHour = {}
    for (let h = 0; h < 24; h += 1) {
      byHour[h] = { hour: h, P0: 0, P1: 0, P2: 0, P3: 0 }
    }
    for (const inc of incidents || []) {
      const ts = inc?.start_time
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
  }, [incidents])

  const topIncidentTypes = useMemo(() => {
    const counts = {}
    for (const inc of incidents || []) {
      const k = inc?.incident_type || 'unknown'
      counts[k] = (counts[k] || 0) + Number(inc?.event_count || 1)
    }
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6)
  }, [incidents])

  const opsImpact = useMemo(() => {
    const totalEvents = (incidents || []).reduce((acc, x) => acc + Number(x?.event_count || 0), 0)
    const p0Incidents = (incidents || []).filter(x => x?.severity === 'P0').length
    const activeIncidents = (incidents || []).length
    const estimatedMttdMin = activeIncidents > 0 ? Math.max(3, Math.round((p0Incidents * 8 + 20) / activeIncidents)) : 0
    return { totalEvents, p0Incidents, activeIncidents, estimatedMttdMin }
  }, [incidents])

  const getSolution = async (c) => {
    setSolution(null)
    setSolutionLoading(true)
    try {
      const { data } = await demoApi.post('/solution', {
        cluster_id: c.cluster_id,
        error_type: c.error_type,
        severity: c.severity,
      })
      setSolution(data)
    } catch (e) {
      console.error(e)
      setErr('Failed to fetch solution from demo API.')
    } finally {
      setSolutionLoading(false)
    }
  }

  const openIncident = (inc) => {
    setSelectedIncident(inc)
    setSolution(null)
  }

  const closeIncident = () => {
    setSelectedIncident(null)
    setSolution(null)
  }

  if (loading) {
    return <div className="min-h-screen bg-slate-50 flex items-center justify-center">Loading dashboard...</div>
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 text-sm text-slate-600">
              <Sparkles className="w-4 h-4" />
              <span>MOZAIC Multi-Source Incident Intelligence</span>
            </div>
            <h1 className="text-3xl font-bold text-slate-900 mt-1">Incident Clustering + Severity + GenAI Assist</h1>
            <p className="text-slate-600 mt-2 max-w-3xl">
              Unified observability across Grafana, Kubernetes, CloudWatch, and Sentry with clustering and remediation guidance.
            </p>

            <div className="mt-4 inline-flex rounded-xl border bg-white p-1">
              {['grafana','k8s','cloudwatch','sentry'].map(s => (
                <button
                  key={s}
                  onClick={() => setSource(s)}
                  className={classNames(
                    'px-3 py-1.5 text-sm rounded-lg',
                    source === s ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
                  )}
                >
                  {s === 'grafana' ? 'Grafana' : s === 'k8s' ? 'Kubernetes' : s === 'cloudwatch' ? 'CloudWatch' : 'Sentry'}
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-xl border bg-white px-4 py-3">
            <div className="text-xs text-slate-500">API</div>
            <div className="font-mono text-sm">http://localhost:8000</div>
          </div>
        </div>

        {err ? (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 mt-0.5" />
            <div>
              <div className="font-semibold">Service not running</div>
              <div className="text-sm mt-1">{err}</div>
            </div>
          </div>
        ) : null}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card title="Points" value={core.num_points ?? '-'} icon={<Activity className="w-5 h-5" />} />
          <Card title="Clusters" value={core.num_clusters ?? '-'} icon={<CheckCircle2 className="w-5 h-5" />} />
          <Card title="Noise" value={core.num_noise ?? '-'} icon={<AlertTriangle className="w-5 h-5" />} />
          <Card title="Silhouette" value={fmt(core.silhouette_score)} icon={<Activity className="w-5 h-5" />} />
        </div>

        <div className="rounded-2xl border bg-white p-5 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Active incidents</h2>
            <div className="text-xs text-slate-500">Correlated incidents across connected telemetry sources</div>
          </div>
          {incidents.length === 0 ? (
            <div className="text-slate-600 text-sm">No incidents loaded yet. Check telemetry ingest and clustering outputs.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {incidents.slice(0, 6).map(inc => (
                <button
                  key={inc.incident_id}
                  onClick={() => openIncident(inc)}
                  className="text-left rounded-2xl border bg-slate-50 hover:bg-slate-100 p-4 transition"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-xs text-slate-500">{inc.incident_id}</div>
                      <div className="font-semibold text-slate-900 mt-1">{inc.incident_type}</div>
                      <div className="text-sm text-slate-700 mt-1">Services: {(inc.affected_services || []).slice(0,2).join(', ') || 'n/a'}</div>
                    </div>
                    <span className={classNames(
                      'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold',
                      inc.severity === 'P0' ? 'bg-red-50 text-red-700' :
                      inc.severity === 'P1' ? 'bg-amber-50 text-amber-700' :
                      'bg-blue-50 text-blue-700'
                    )}>
                      {inc.severity}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                    <span>Events: {inc.event_count ?? '-'}</span>
                    <span>Correlation: {inc.correlation_id ?? '-'}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2 rounded-2xl border bg-white p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-slate-900">Top clusters (by size)</h2>
              <div className="text-xs text-slate-500">Source: {source}</div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topBars}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="size" radius={[6, 6, 0, 0]}>
                    {topBars.map((e, idx) => (
                      <Cell key={idx} fill={COLORS[e.severity] || '#64748b'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 text-xs text-slate-500">
              Color shows severity (P0 red, P1 amber, P2 blue).
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Severity distribution (P0/P1/P2)</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={severityPie} dataKey="value" nameKey="name" outerRadius={90}>
                    {severityPie.map((entry, index) => (
                      <Cell key={index} fill={COLORS[entry.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-3 text-xs">
              {severityPie.map(s => (
                <div key={s.name} className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[s.name] || '#64748b' }} />
                  <span className="text-slate-700">{s.name}</span>
                  <span className="text-slate-500">{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Cluster Coverage</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={noiseBreakdown} dataKey="value" nameKey="name" outerRadius={90}>
                    {noiseBreakdown.map((entry, index) => (
                      <Cell key={index} fill={entry.name === 'Noise' ? '#ef4444' : '#0f766e'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-xs text-slate-500">
              Clustered: {clusteredPoints} | Noise: {noisePoints}
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Operational Impact</h2>
            <div className="grid grid-cols-2 gap-3">
              <Stat title="Active incidents" value={opsImpact.activeIncidents} />
              <Stat title="Total events" value={opsImpact.totalEvents} />
              <Stat title="P0 incidents" value={opsImpact.p0Incidents} />
              <Stat title="Est. MTTD (min)" value={opsImpact.estimatedMttdMin} />
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Error type distribution (free-text labels)</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={errorTypes.map(e => ({ name: e.error_type, count: e.count, severity: e.severity }))}>
                  <XAxis dataKey="name" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {errorTypes.map((e, idx) => (
                      <Cell key={idx} fill={COLORS[e.severity] || '#64748b'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-xs text-slate-500">Hover bars to see error type + counts.</div>
          </div>

          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Uptime over the day</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={uptime}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="uptime" stroke="#0f172a" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-xs text-slate-500">Computed from synthetic metadata (1 - anomaly rate per hour).</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Severity Trend by Hour</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={severityTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="P0" stroke={COLORS.P0} strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="P1" stroke={COLORS.P1} strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="P2" stroke={COLORS.P2} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5">
            <h2 className="font-semibold text-slate-900 mb-3">Top Incident Types</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topIncidentTypes}>
                  <XAxis dataKey="name" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#334155" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Clusters</h2>
            <div className="text-xs text-slate-500">Click "Get solution" to generate remediation guidance</div>
          </div>

          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b">
                  <th className="py-2 pr-4">Cluster</th>
                  <th className="py-2 pr-4">Size</th>
                  <th className="py-2 pr-4">Severity</th>
                  <th className="py-2 pr-4">Cluster classification</th>
                  <th className="py-2 pr-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {clusters.map(c => (
                  <tr key={c.cluster_id} className="border-b last:border-b-0">
                    <td className="py-2 pr-4 font-medium">C{c.cluster_id}</td>
                    <td className="py-2 pr-4">{c.size}</td>
                    <td className="py-2 pr-4">
                      <span className={classNames(
                        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold',
                        c.severity === 'P0' ? 'bg-red-50 text-red-700' :
                        c.severity === 'P1' ? 'bg-amber-50 text-amber-700' :
                        'bg-blue-50 text-blue-700'
                      )}>
                        {c.severity}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-slate-700">{c.error_type}</td>
                    <td className="py-2 pr-4">
                      <button
                        onClick={() => getSolution(c)}
                        className="rounded-lg bg-slate-900 text-white px-3 py-1.5 hover:bg-slate-800"
                      >
                        Get solution
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-5 rounded-xl border bg-slate-50 p-4">
            <div className="font-semibold text-slate-900 mb-2">Solution output</div>
            {solutionLoading ? (
              <div className="text-slate-600">Loading...</div>
            ) : solution ? (
              <div>
                <div className="text-sm text-slate-700 mb-2">
                  Cluster <span className="font-mono">{solution.cluster_id}</span> - <span className="font-semibold">{solution.severity}</span> - <span className="font-mono">{solution.error_type}</span>
                </div>
                <ol className="list-decimal pl-5 text-sm text-slate-800 space-y-1">
                  {solution.recommended_actions?.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ol>
                <div className="text-xs text-slate-500 mt-2">{solution.note}</div>
              </div>
            ) : (
              <div className="text-slate-600">Click "Get solution" on a cluster to get remediation steps.</div>
            )}
          </div>
        </div>

        <div className="text-xs text-slate-500 mt-6">
          Operational insight generated from available telemetry outputs.
        </div>

        {selectedIncident ? (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
            <div className="w-full max-w-3xl rounded-2xl bg-white border shadow-xl overflow-hidden">
              <div className="p-5 border-b flex items-start justify-between gap-4">
                <div>
                  <div className="text-xs text-slate-500">Incident</div>
                  <div className="text-xl font-bold text-slate-900">{selectedIncident.incident_type}</div>
                  <div className="text-sm text-slate-600 mt-1">{selectedIncident.incident_id} - {selectedIncident.correlation_id}</div>
                </div>
                <button onClick={closeIncident} className="rounded-lg px-3 py-1.5 hover:bg-slate-100">Close</button>
              </div>

              <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <div className="font-semibold text-slate-900 mb-2">Summary</div>
                  <div className="text-sm text-slate-700 space-y-1">
                    <div><span className="text-slate-500">Severity:</span> <span className="font-semibold">{selectedIncident.severity}</span></div>
                    <div><span className="text-slate-500">Services:</span> {(selectedIncident.affected_services || []).join(', ') || 'n/a'}</div>
                    <div><span className="text-slate-500">Event count:</span> {selectedIncident.event_count ?? '-'}</div>
                    <div><span className="text-slate-500">Window:</span> {selectedIncident.start_time} - {selectedIncident.end_time}</div>
                  </div>

                  <div className="mt-4">
                    <button
                      onClick={() => getSolution({ cluster_id: 0, error_type: selectedIncident.incident_type, severity: selectedIncident.severity })}
                      className="rounded-xl bg-slate-900 text-white px-4 py-2 hover:bg-slate-800"
                    >
                      Give solution
                    </button>
                    {solutionLoading ? <div className="text-sm text-slate-600 mt-2">Generating remediation plan...</div> : null}
                  </div>

                  {solution ? (
                    <div className="mt-4 rounded-xl border bg-slate-50 p-4">
                      <div className="font-semibold text-slate-900">Recommended actions</div>
                      <ol className="list-decimal pl-5 text-sm text-slate-800 space-y-1 mt-2">
                        {solution.recommended_actions?.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ol>
                      <div className="text-xs text-slate-500 mt-2">{solution.note}</div>
                    </div>
                  ) : null}
                </div>

                <div>
                  <div className="font-semibold text-slate-900 mb-2">Evidence (raw log samples)</div>
                  {logSamples.length === 0 ? (
                    <div className="text-sm text-slate-600">No samples loaded for this source yet.</div>
                  ) : (
                    <div className="space-y-2">
                      {logSamples.slice(0, 5).map((s, i) => (
                        <pre key={i} className="text-xs bg-slate-950 text-slate-100 rounded-xl p-3 overflow-auto max-h-40">{s}</pre>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}

function Card({ title, value, icon }) {
  return (
    <div className="rounded-2xl border bg-white p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-slate-500">{title}</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{value}</div>
        </div>
        <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700">
          {icon}
        </div>
      </div>
    </div>
  )
}

function Stat({ title, value }) {
  return (
    <div className="rounded-xl border bg-slate-50 p-3">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="text-xl font-bold text-slate-900 mt-1">{value}</div>
    </div>
  )
}

function fmt(x) {
  if (x === null || x === undefined) return '-'
  const n = Number(x)
  if (Number.isNaN(n)) return '-'
  return n.toFixed(3)
}
