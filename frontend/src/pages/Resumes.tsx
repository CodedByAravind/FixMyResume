import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createResume, deleteResume, listResumes } from '../api/resumes'
import type { ResumeSummary } from '../types/resume'
import { useAuth } from '../context/AuthContext'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import EmptyState from '../components/ui/EmptyState'

function Resumes() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [resumes, setResumes] = useState<ResumeSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<ResumeSummary | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    listResumes()
      .then(setResumes)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load resumes'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleCreate = async () => {
    try {
      const resume = await createResume({})
      navigate(`/resumes/${resume.id}/edit`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create resume')
    }
  }

  const handleDelete = async () => {
    if (!deleting) return
    try {
      await deleteResume(deleting.id)
      setDeleting(null)
      load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete resume')
      setDeleting(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Resumes</h1>
            <p className="text-gray-600">Welcome back, {user?.name}</p>
          </div>
          <div className="flex space-x-3">
            <Link to="/" className="bg-gray-200 text-gray-700 rounded-md px-4 py-2 hover:bg-gray-300">
              Home
            </Link>
            <button onClick={handleCreate} className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700">
              New Resume
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {loading && <p className="text-gray-500 text-center py-12">Loading resumes...</p>}

        {!loading && resumes.length === 0 && (
          <EmptyState
            title="No resumes yet"
            message="Create your first resume to get started."
            actionLabel="Create Resume"
            onAction={handleCreate}
          />
        )}

        {!loading && resumes.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2">
            {resumes.map((r) => (
              <div key={r.id} className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-1">{r.title}</h2>
                <p className="text-sm text-gray-500 mb-4">
                  Updated {new Date(r.updated_at).toLocaleDateString()}
                </p>
                <div className="flex space-x-2">
                  <Link to={`/resumes/${r.id}`} className="bg-gray-200 text-gray-700 rounded-md px-3 py-1.5 text-sm hover:bg-gray-300">
                    View
                  </Link>
                  <Link to={`/resumes/${r.id}/edit`} className="bg-blue-600 text-white rounded-md px-3 py-1.5 text-sm hover:bg-blue-700">
                    Edit
                  </Link>
                  <button
                    onClick={() => setDeleting(r)}
                    className="bg-red-100 text-red-700 rounded-md px-3 py-1.5 text-sm hover:bg-red-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <ConfirmDialog
          open={!!deleting}
          title="Delete resume?"
          message={`This will permanently delete "${deleting?.title}" and all of its sections. This cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleting(null)}
        />
      </div>
    </div>
  )
}

export default Resumes
