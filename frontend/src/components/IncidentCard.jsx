export default function IncidentCard({ incident }) {
  const severityColors = {
    low: 'bg-blue-500/10 text-blue-200 ring-1 ring-blue-500/30',
    medium: 'bg-amber-500/10 text-amber-200 ring-1 ring-amber-500/30',
    high: 'bg-orange-500/10 text-orange-200 ring-1 ring-orange-500/30',
    critical: 'bg-red-500/10 text-red-200 ring-1 ring-red-500/30'
  }

  return (
    <div className="bg-slate-900/70 text-white rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold">{incident.title}</h3>
          <p className="text-sm text-slate-300">Source: {incident.source}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${severityColors[incident.severity]}`}>
          {incident.severity.toUpperCase()}
        </span>
      </div>
      <p className="text-sm text-slate-400 mb-2">
        {new Date(incident.timestamp).toLocaleString()}
      </p>
      {incident.correlation_data && (
        <div className="mt-3 text-sm text-slate-200">
          <span className="font-medium">Cluster ID:</span> {incident.correlation_data.cluster_id} | 
          <span className="font-medium"> Logs:</span> {incident.correlation_data.log_count}
        </div>
      )}
    </div>
  )
}