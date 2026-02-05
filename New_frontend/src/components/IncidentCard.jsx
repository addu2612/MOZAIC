export default function IncidentCard({ incident }) {
  const severityColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold">{incident.title}</h3>
          <p className="text-sm text-gray-600">Source: {incident.source}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${severityColors[incident.severity]}`}>
          {incident.severity.toUpperCase()}
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-2">
        {new Date(incident.timestamp).toLocaleString()}
      </p>
      {incident.correlation_data && (
        <div className="mt-3 text-sm text-gray-700">
          <span className="font-medium">Cluster ID:</span> {incident.correlation_data.cluster_id} | 
          <span className="font-medium"> Logs:</span> {incident.correlation_data.log_count}
        </div>
      )}
    </div>
  )
}