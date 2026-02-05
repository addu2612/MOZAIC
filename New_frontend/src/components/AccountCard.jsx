export default function AccountCard({ account, onDelete }) {
  const statusColors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    error: 'bg-red-100 text-red-800'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold capitalize">{account.service_type}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[account.status]}`}>
          {account.status}
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3">
        Connected: {new Date(account.created_at).toLocaleDateString()}
      </p>
      <button
        onClick={() => onDelete(account.id)}
        className="text-red-600 hover:text-red-800 text-sm"
      >
        Delete
      </button>
    </div>
  )
}