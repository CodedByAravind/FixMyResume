import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { deleteResume, getResume } from '../api/resumes'
import type { Resume } from '../types/resume'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import EmptyState from '../components/ui/EmptyState'

function ResumeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)

  useEffect(() => {
    if (!id) return
    getResume(Number(id))
      .then(setResume)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load resume'))
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!resume) return
    try {
      await deleteResume(resume.id)
      navigate('/resumes', { replace: true })
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete resume')
      setConfirmDelete(false)
    }
  }

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  }

  if (error && !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <EmptyState title="Resume not found" message={error} />
          <div className="text-center mt-4">
            <Link to="/resumes" className="text-blue-600 hover:underline">Back to resumes</Link>
          </div>
        </div>
      </div>
    )
  }

  if (!resume) return null

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link to="/resumes" className="text-blue-600 hover:underline text-sm">← Back to resumes</Link>
            <h1 className="text-3xl font-bold text-gray-900 mt-1">{resume.title}</h1>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setConfirmDelete(true)}
              className="bg-red-100 text-red-700 rounded-md px-4 py-2 hover:bg-red-200"
            >
              Delete
            </button>
            <Link
              to={`/resumes/${resume.id}/edit`}
              className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700"
            >
              Edit
            </Link>
            <Link
              to={`/resumes/${resume.id}/versions`}
              className="bg-indigo-600 text-white rounded-md px-4 py-2 hover:bg-indigo-700"
            >
              Versions
            </Link>
            <Link
              to={`/resumes/${resume.id}/analyze`}
              className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
            >
              Analyze Job
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {resume.full_name && (
              <div><dt className="text-sm text-gray-500">Name</dt><dd className="font-medium">{resume.full_name}</dd></div>
            )}
            {resume.email && (
              <div><dt className="text-sm text-gray-500">Email</dt><dd className="font-medium">{resume.email}</dd></div>
            )}
            {resume.phone && (
              <div><dt className="text-sm text-gray-500">Phone</dt><dd className="font-medium">{resume.phone}</dd></div>
            )}
            {resume.location && (
              <div><dt className="text-sm text-gray-500">Location</dt><dd className="font-medium">{resume.location}</dd></div>
            )}
            {resume.website && (
              <div><dt className="text-sm text-gray-500">Website</dt><dd className="font-medium"><a href={resume.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{resume.website}</a></dd></div>
            )}
            {resume.linkedin && (
              <div><dt className="text-sm text-gray-500">LinkedIn</dt><dd className="font-medium"><a href={resume.linkedin} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{resume.linkedin}</a></dd></div>
            )}
            {resume.github && (
              <div><dt className="text-sm text-gray-500">GitHub</dt><dd className="font-medium"><a href={resume.github} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{resume.github}</a></dd></div>
            )}
          </dl>
          {resume.summary && (
            <div className="mt-4">
              <dt className="text-sm text-gray-500">Summary</dt>
              <dd className="whitespace-pre-wrap">{resume.summary}</dd>
            </div>
          )}
        </div>

        <div className="space-y-6">
          {resume.education.length > 0 && (
            <SectionBlock title="Education">
              {resume.education.map((e) => (
                <li key={e.id} className="mb-3">
                  <p className="font-semibold">{e.institution}</p>
                  <p className="text-sm text-gray-600">{[e.degree, e.field_of_study].filter(Boolean).join(' - ')}</p>
                  {(e.start_date || e.end_date) && <p className="text-sm text-gray-500">{[e.start_date, e.end_date].filter(Boolean).join(' to ')}</p>}
                </li>
              ))}
            </SectionBlock>
          )}
          {resume.experience.length > 0 && (
            <SectionBlock title="Work Experience">
              {resume.experience.map((x) => (
                <li key={x.id} className="mb-3">
                  <p className="font-semibold">{x.title} — {x.company}</p>
                  {(x.start_date || x.end_date) && <p className="text-sm text-gray-500">{[x.start_date, x.end_date].filter(Boolean).join(' to ')}</p>}
                  {x.description && <p className="text-sm text-gray-600 whitespace-pre-wrap">{x.description}</p>}
                </li>
              ))}
            </SectionBlock>
          )}
          {resume.projects.length > 0 && (
            <SectionBlock title="Projects">
              {resume.projects.map((p) => (
                <li key={p.id} className="mb-3">
                  <p className="font-semibold">{p.name}</p>
                  {p.url && <a href={p.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline text-sm">{p.url}</a>}
                  {p.description && <p className="text-sm text-gray-600 whitespace-pre-wrap">{p.description}</p>}
                </li>
              ))}
            </SectionBlock>
          )}
          {resume.skills.length > 0 && (
            <SectionBlock title="Skills">
              <div className="flex flex-wrap gap-2">
                {resume.skills.map((s) => (
                  <span key={s.id} className="bg-blue-50 text-blue-700 rounded-full px-3 py-1 text-sm">
                    {s.name}{s.category ? ` (${s.category})` : ''}
                  </span>
                ))}
              </div>
            </SectionBlock>
          )}
          {resume.certifications.length > 0 && (
            <SectionBlock title="Certifications">
              {resume.certifications.map((c) => (
                <li key={c.id} className="mb-3">
                  <p className="font-semibold">{c.name}</p>
                  <p className="text-sm text-gray-600">{c.issuer}{c.date_obtained ? ` · ${c.date_obtained}` : ''}</p>
                </li>
              ))}
            </SectionBlock>
          )}
        </div>

        <ConfirmDialog
          open={confirmDelete}
          title="Delete resume?"
          message={`This will permanently delete "${resume.title}". This cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(false)}
        />
      </div>
    </div>
  )
}

function SectionBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <ul className="list-none">{children}</ul>
    </div>
  )
}

export default ResumeDetail
