export default function ProjectCard({ project, onDelete, onClick }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
      <div onClick={onClick}>
        <h3 className="text-xl font-bold mb-2">{project.name}</h3>
        <p className="text-gray-600 text-sm mb-4">{project.description || 'No description'}</p>
        <p className="text-xs text-gray-500">
          Created: {new Date(project.created_at).toLocaleDateString()}
        </p>
      </div>
      <button
        onClick={(e) => { e.stopPropagation(); onDelete(project.id) }}
        className="mt-4 text-red-600 hover:text-red-800 text-sm"
      >
        Delete
      </button>
    </div>
  )
}