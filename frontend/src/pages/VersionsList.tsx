import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { deleteVersion, listVersions } from '../api/versions'
import type { VersionSummary } from '../types/resume_version'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import EmptyState from '../components/ui/EmptyState'

function VersionsList() {
  const { id } = useParams()
  const resumeId = Number(id)
  const [versions, setVersions] = useState<VersionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<VersionSummary | null>(null)

  const load = () => {
    setLoading(true)
    setError(null)
    listVersions(resumeId)
      .then(setVersions)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load versions'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [resumeId])

  const handleDelete = async () => {
    if (!deleting) return
    try {
      await deleteVersion(resumeId, deleting.id)
      setDeleting(null)
      load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete version')
      setDeleting(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to={`/resumes/${resumeId}`} className="text-blue-600 hover:underline text-sm">Back to resume</Link>
            <h1 className="text-3xl font-bold text-gray-900 mt-1">Tailored Versions</h1>
          </div>
          <Link to={`/resumes/${resumeId}/tailor`} className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700">
            New Tailored Version
          </Link>
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded p-3 mb-4"><p className="text-red-600">{error}</p></div>}

        {loading && <p className="text-gray-500 text-center py-12">Loading versions...</p>}

        {!loading && versions.length === 0 && (
          <EmptyState
            title="No tailored versions yet"
            message="Tailor this resume against a job description to create a version."
            actionLabel="Tailor Resume"
          />
        )}

        {!loading && versions.length > 0 && (
          <div className="space-y-3">
            {versions.map((v) => (
              <div key={v.id} className="bg-white rounded-lg shadow-md p-5 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{v.name}</p>
                  <p className="text-sm text-gray-500">Score {v.analysis_score ?? 'n/a'} → tailored {v.tailored_score ?? 'n/a'} · {new Date(v.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex space-x-2">
                  <Link to={`/resumes/${resumeId}/versions/${v.id}/compare`} className="bg-gray-200 text-gray-700 rounded px-3 py-1.5 text-sm hover:bg-gray-300">Compare</Link>
                  <Link to={`/resumes/${resumeId}/versions/${v.id}`} className="bg-blue-600 text-white rounded px-3 py-1.5 text-sm hover:bg-blue-700">View</Link>
                  <button onClick={() => setDeleting(v)} className="bg-red-100 text-red-700 rounded px-3 py-1.5 text-sm hover:bg-red-200">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <ConfirmDialog
        open={!!deleting}
        title="Delete version?"
        message={`Delete "${deleting?.name}"? This cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}

export default VersionsList
