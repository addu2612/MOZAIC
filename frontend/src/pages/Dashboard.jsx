import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import ProjectCard from '../components/ProjectCard'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [newProject, setNewProject] = useState({ name: '', description: '' })
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const { data } = await api.get('/projects/')
      setProjects(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await api.post('/projects/', newProject)
      setShowModal(false)
      setNewProject({ name: '', description: '' })
      fetchProjects()
    } catch (err) {
      console.error(err)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this project?')) return
    try {
      await api.delete(`/projects/${id}`)
      fetchProjects()
    } catch (err) {
      console.error(err)
    }
  }

  if (loading) return <div className="flex justify-center items-center h-screen bg-slate-950 text-slate-300">Loading...</div>

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(16,185,129,0.15),_transparent_40%)]" />
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 text-blue-200 px-3 py-1 text-xs font-semibold ring-1 ring-blue-500/30">
              Workspace
            </div>
            <h1 className="text-3xl font-bold mt-4">Projects</h1>
            <p className="text-slate-300 text-sm mt-1">Manage your monitored environments and services.</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-white text-slate-900 px-4 py-2.5 rounded-xl font-semibold hover:bg-slate-200 transition"
          >
            Create Project
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center py-16 text-slate-300 bg-slate-900/70 rounded-3xl shadow-2xl ring-1 ring-slate-800">
            <div className="text-white font-semibold mb-2">No projects yet</div>
            <div className="text-sm">Create your first project to start monitoring incidents.</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map(project => (
              <ProjectCard
                key={project.id}
                project={project}
                onDelete={handleDelete}
                onClick={() => navigate(`/project/${project.id}`)}
              />
            ))}
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 text-white rounded-3xl p-6 max-w-md w-full shadow-2xl ring-1 ring-slate-800">
              <h2 className="text-xl font-bold mb-4">Create Project</h2>
              <form onSubmit={handleCreate}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Name</label>
                  <input
                    type="text"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-3 py-2.5 border border-slate-700 rounded-xl bg-slate-950 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                  <textarea
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="w-full px-3 py-2.5 border border-slate-700 rounded-xl bg-slate-950 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                    rows="3"
                  />
                </div>
                <div className="flex gap-2">
                  <button type="submit" className="flex-1 bg-white text-slate-900 py-2.5 rounded-xl font-semibold hover:bg-slate-200">
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 bg-slate-800 text-slate-200 py-2.5 rounded-xl font-semibold hover:bg-slate-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}