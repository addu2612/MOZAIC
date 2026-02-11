export default function AccountCard({ account, onDelete }) {
  const statusColors = {
    active: 'bg-emerald-500/10 text-emerald-200 ring-1 ring-emerald-500/30',
    inactive: 'bg-slate-500/10 text-slate-200 ring-1 ring-slate-500/30',
    error: 'bg-red-500/10 text-red-200 ring-1 ring-red-500/30'
  }

  return (
    <div className="bg-slate-900/70 text-white rounded-2xl shadow-2xl ring-1 ring-slate-800 p-4">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold capitalize">{account.service_type}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[account.status]}`}>
          {account.status}
        </span>
      </div>
      <p className="text-sm text-slate-300 mb-3">
        Connected: {new Date(account.created_at).toLocaleDateString()}
      </p>
      <button
        onClick={() => onDelete(account.id)}
        className="text-red-200 hover:text-red-100 text-sm font-semibold"
      >
        Delete
      </button>
    </div>
  )
}