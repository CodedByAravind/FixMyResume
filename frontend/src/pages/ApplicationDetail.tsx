import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { deleteApplication, getApplication, updateApplication } from '../api/applications'
import { APPLICATION_STATUSES } from '../types/application'
import type { JobApplication } from '../types/application'
import ConfirmDialog from '../components/ui/ConfirmDialog'

function ApplicationDetail() {
  const { id } = useParams()
  const appId = Number(id)
  const navigate = useNavigate()
  const [app, setApp] = useState<JobApplication | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notes, setNotes] = useState('')
  const [status, setStatus] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getApplication(appId)
      .then((a) => { setApp(a); setNotes(a.notes ?? ''); setStatus(a.status) })
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load application'))
      .finally(() => setLoading(false))
  }, [appId])

  const save = async () => {
    setSaving(true)
    setError(null)
    try {
      const updated = await updateApplication(appId, { status, notes })
      setApp(updated)
      setNotes(updated.notes ?? '')
      setStatus(updated.status)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update')
    } finally {
      setSaving(false)
    }
  }

  const remove = async () => {
    try {
      await deleteApplication(appId)
      navigate('/applications')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete')
      setConfirmDelete(false)
    }
  }

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  if (error && !app) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-red-600">{error}</div>
  if (!app) return null

  const fmt = (s?: string | null) => (s ? new Date(s).toLocaleString() : '—')

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <Link to="/applications" className="text-blue-600 hover:underline text-sm">Back to applications</Link>
        <div className="flex items-center justify-between mt-1 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">{app.company} — {app.job_title}</h1>
          <button onClick={() => setConfirmDelete(true)} className="bg-red-100 text-red-700 rounded-md px-4 py-2 hover:bg-red-200">Delete</button>
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded p-3 mb-4"><p className="text-red-600">{error}</p></div>}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6 space-y-2">
          <p><span className="font-medium">Status:</span> {app.status}</p>
          <p><span className="font-medium">Applied:</span> {fmt(app.application_date)}</p>
          <p><span className="font-medium">Interview:</span> {fmt(app.interview_date)}</p>
          <p><span className="font-medium">Created:</span> {fmt(app.created_at)}</p>
          <p><span className="font-medium">Last updated:</span> {fmt(app.updated_at)}</p>
          {app.job_url && <p><span className="font-medium">URL:</span> <a href={app.job_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{app.job_url}</a></p>}
          {app.location && <p><span className="font-medium">Location:</span> {app.location}</p>}
          <p><span className="font-medium">Resume ID:</span> {app.resume_id}{app.resume_version_id ? ` · Version ${app.resume_version_id}` : ' · live resume'}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
              {APPLICATION_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea rows={5} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <button onClick={save} disabled={saving} className="bg-blue-600 text-white rounded-md px-5 py-2 hover:bg-blue-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <ConfirmDialog
          open={confirmDelete}
          title="Delete application?"
          message={`Delete "${app.company} — ${app.job_title}"? This cannot be undone.`}
          onConfirm={remove}
          onCancel={() => setConfirmDelete(false)}
        />
      </div>
    </div>
  )
}

export default ApplicationDetail
