import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { createApplication, getApplication, updateApplication } from '../api/applications'
import { listResumes } from '../api/resumes'
import { listVersions } from '../api/versions'
import { APPLICATION_STATUSES } from '../types/application'

function ApplicationForm() {
  const { id } = useParams()
  const editId = id ? Number(id) : null
  const navigate = useNavigate()

  const [resumes, setResumes] = useState<{ id: number; title: string }[]>([])
  const [versions, setVersions] = useState<{ id: number; name: string }[]>([])
  const [resumeId, setResumeId] = useState('')
  const [versionId, setVersionId] = useState('')
  const [form, setForm] = useState({
    company: '', job_title: '', job_url: '', location: '', status: 'applied',
    application_date: '', interview_date: '', notes: '',
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listResumes()
      .then((rs) => setResumes(rs.map((r) => ({ id: r.id, title: r.title }))))
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load resumes'))
  }, [])

  // Load existing app when editing
  useEffect(() => {
    if (!editId) return
    getApplication(editId)
      .then((a) => {
        setResumeId(String(a.resume_id))
        setVersionId(a.resume_version_id ? String(a.resume_version_id) : '')
        setForm({
          company: a.company, job_title: a.job_title, job_url: a.job_url ?? '',
          location: a.location ?? '', status: a.status,
          application_date: a.application_date ? a.application_date.slice(0, 16) : '',
          interview_date: a.interview_date ? a.interview_date.slice(0, 16) : '',
          notes: a.notes ?? '',
        })
      })
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load application'))
  }, [editId])

  // Load versions for the selected resume
  useEffect(() => {
    if (!resumeId) {
      setVersions([])
      return
    }
    listVersions(Number(resumeId))
      .then((vs) => setVersions(vs.map((v) => ({ id: v.id, name: v.name }))))
      .catch(() => setVersions([]))
  }, [resumeId])

  const set = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    const payload: any = {
      resume_id: Number(resumeId),
      resume_version_id: versionId ? Number(versionId) : null,
      company: form.company,
      job_title: form.job_title,
      job_url: form.job_url || undefined,
      location: form.location || undefined,
      status: form.status,
      application_date: form.application_date || undefined,
      interview_date: form.status === 'interview' && form.interview_date ? form.interview_date : undefined,
      notes: form.notes || undefined,
    }
    try {
      const saved = editId
        ? await updateApplication(editId, payload)
        : await createApplication(payload)
      navigate(`/applications/${saved.id}`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to save application')
    } finally {
      setBusy(false)
    }
  }

  const input = 'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500'

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <Link to="/applications" className="text-blue-600 hover:underline text-sm">Back to applications</Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-1 mb-6">{editId ? 'Edit Application' : 'New Application'}</h1>
        {error && <div className="bg-red-50 border border-red-200 rounded p-3 mb-4"><p className="text-red-600">{error}</p></div>}

        <form onSubmit={submit} className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Resume *</label>
            <select className={input} value={resumeId} onChange={(e) => { setResumeId(e.target.value); setVersionId('') }} required>
              <option value="">Select a resume</option>
              {resumes.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tailored version (optional)</label>
            <select className={input} value={versionId} onChange={(e) => setVersionId(e.target.value)} disabled={!resumeId}>
              <option value="">Use live resume (no tailored version)</option>
              {versions.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Company *</label><input className={input} value={form.company} onChange={(e) => set('company', e.target.value)} required /></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label><input className={input} value={form.job_title} onChange={(e) => set('job_title', e.target.value)} required /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Job URL</label><input className={input} value={form.job_url} onChange={(e) => set('job_url', e.target.value)} /></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Location</label><input className={input} value={form.location} onChange={(e) => set('location', e.target.value)} /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select className={input} value={form.status} onChange={(e) => set('status', e.target.value)}>
                {APPLICATION_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Applied date</label><input type="datetime-local" className={input} value={form.application_date} onChange={(e) => set('application_date', e.target.value)} /></div>
          </div>
          {form.status === 'interview' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Interview date</label>
              <input type="datetime-local" className={input} value={form.interview_date} onChange={(e) => set('interview_date', e.target.value)} />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea rows={4} className={input} value={form.notes} onChange={(e) => set('notes', e.target.value)} />
          </div>
          <button type="submit" disabled={busy || !resumeId} className="bg-blue-600 text-white rounded-md px-5 py-2 hover:bg-blue-700 disabled:opacity-50">
            {busy ? 'Saving...' : 'Save Application'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default ApplicationForm
