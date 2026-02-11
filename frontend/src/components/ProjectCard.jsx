export default function ProjectCard({ project, onDelete, onClick }) {
  return (
    <div className="group bg-slate-900/70 text-white rounded-3xl shadow-2xl ring-1 ring-slate-800 p-6 hover:ring-slate-700 transition cursor-pointer">
      <div onClick={onClick}>
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-2.5 py-1 text-xs font-semibold ring-1 ring-blue-500/30 mb-4">
          Project
        </div>
        <h3 className="text-xl font-bold mb-2">{project.name}</h3>
        <p className="text-slate-300 text-sm mb-4">{project.description || 'No description'}</p>
        <p className="text-xs text-slate-400">
          Created: {new Date(project.created_at).toLocaleDateString()}
        </p>
      </div>
      <button
        onClick={(e) => { e.stopPropagation(); onDelete(project.id) }}
        className="mt-5 inline-flex items-center gap-2 text-red-200 hover:text-red-100 text-sm font-semibold"
      >
        Delete
      </button>
    </div>
  )
}