import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  createCertification,
  createEducation,
  createExperience,
  createProject,
  createSkill,
  deleteCertification,
  deleteEducation,
  deleteExperience,
  deleteProject,
  deleteSkill,
  getResume,
  updateCertification,
  updateEducation,
  updateExperience,
  updateProject,
  updateResume,
  updateSkill,
} from '../api/resumes'
import SectionEditor from '../components/resume/SectionEditor'
import type { Resume } from '../types/resume'

function ResumeEditor() {
  const { id } = useParams<{ id: string }>()
  const resumeId = Number(id)
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [details, setDetails] = useState({
    title: '',
    full_name: '',
    email: '',
    phone: '',
    location: '',
    website: '',
    linkedin: '',
    github: '',
    summary: '',
  })
  const [savingDetails, setSavingDetails] = useState(false)
  const [detailsError, setDetailsError] = useState<string | null>(null)
  const [detailsSaved, setDetailsSaved] = useState(false)

  useEffect(() => {
    if (!id) return
    getResume(resumeId)
      .then((r) => {
        setResume(r)
        setDetails({
          title: r.title,
          full_name: r.full_name ?? '',
          email: r.email ?? '',
          phone: r.phone ?? '',
          location: r.location ?? '',
          website: r.website ?? '',
          linkedin: r.linkedin ?? '',
          github: r.github ?? '',
          summary: r.summary ?? '',
        })
      })
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load resume'))
      .finally(() => setLoading(false))
  }, [id])

  const handleSaveDetails = async () => {
    setDetailsError(null)
    setDetailsSaved(false)
    setSavingDetails(true)
    try {
      const updated = await updateResume(resumeId, details)
      setResume(updated)
      setDetailsSaved(true)
    } catch (err: any) {
      setDetailsError(err?.response?.data?.detail || 'Failed to save details')
    } finally {
      setSavingDetails(false)
    }
  }

  const setDetail = (key: keyof typeof details, value: string) => {
    setDetails((prev) => ({ ...prev, [key]: value }))
  }

  const inputClass =
    'w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500'

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  }

  if (error && !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-600">{error}</p>
          <Link to="/resumes" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
            Back to resumes
          </Link>
        </div>
      </div>
    )
  }

  if (!resume) return null

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <Link to={`/resumes/${resume.id}`} className="text-blue-600 hover:underline text-sm">
            View resume
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-1">Edit Resume</h1>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Personal details */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Resume Details</h2>
          {detailsError && (
            <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
              <p className="text-red-600">{detailsError}</p>
            </div>
          )}
          {detailsSaved && (
            <div className="bg-green-50 border border-green-200 rounded p-3 mb-4">
              <p className="text-green-700">Details saved.</p>
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input className={inputClass} value={details.title} onChange={(e) => setDetail('title', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input className={inputClass} value={details.full_name} onChange={(e) => setDetail('full_name', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" className={inputClass} value={details.email} onChange={(e) => setDetail('email', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input className={inputClass} value={details.phone} onChange={(e) => setDetail('phone', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input className={inputClass} value={details.location} onChange={(e) => setDetail('location', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
              <input className={inputClass} value={details.website} onChange={(e) => setDetail('website', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">LinkedIn</label>
              <input className={inputClass} value={details.linkedin} onChange={(e) => setDetail('linkedin', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">GitHub</label>
              <input className={inputClass} value={details.github} onChange={(e) => setDetail('github', e.target.value)} />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
              <textarea
                rows={4}
                className={inputClass}
                value={details.summary}
                onChange={(e) => setDetail('summary', e.target.value)}
              />
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={handleSaveDetails}
              disabled={savingDetails}
              className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
            >
              {savingDetails ? 'Saving...' : 'Save Details'}
            </button>
          </div>
        </div>

        {/* Sections */}
        <SectionEditor
          title="Education"
          entries={resume.education}
          fields={[
            { key: 'institution', label: 'Institution *', required: true },
            { key: 'degree', label: 'Degree' },
            { key: 'field_of_study', label: 'Field of Study' },
            { key: 'start_date', label: 'Start (YYYY-MM)', type: 'month' },
            { key: 'end_date', label: 'End (YYYY-MM)', type: 'month' },
            { key: 'description', label: 'Description', type: 'textarea', span: true },
          ]}
          onCreate={async (data) => createEducation(resumeId, data as any)}
          onUpdate={(entryId, data) => updateEducation(resumeId, entryId, data)}
          onDelete={(entryId) => deleteEducation(resumeId, entryId)}
        />

        <SectionEditor
          title="Work Experience"
          entries={resume.experience}
          fields={[
            { key: 'company', label: 'Company *', required: true },
            { key: 'title', label: 'Job Title *', required: true },
            { key: 'location', label: 'Location' },
            { key: 'start_date', label: 'Start (YYYY-MM)', type: 'month' },
            { key: 'end_date', label: 'End (YYYY-MM)', type: 'month' },
            { key: 'description', label: 'Description', type: 'textarea', span: true },
          ]}
          onCreate={async (data) => createExperience(resumeId, data as any)}
          onUpdate={(entryId, data) => updateExperience(resumeId, entryId, data)}
          onDelete={(entryId) => deleteExperience(resumeId, entryId)}
        />

        <SectionEditor
          title="Projects"
          entries={resume.projects}
          fields={[
            { key: 'name', label: 'Project Name *', required: true },
            { key: 'url', label: 'URL', type: 'url' },
            { key: 'description', label: 'Description', type: 'textarea', span: true },
          ]}
          onCreate={async (data) => createProject(resumeId, data as any)}
          onUpdate={(entryId, data) => updateProject(resumeId, entryId, data)}
          onDelete={(entryId) => deleteProject(resumeId, entryId)}
        />

        <SectionEditor
          title="Skills"
          entries={resume.skills}
          fields={[
            { key: 'name', label: 'Skill *', required: true },
            { key: 'category', label: 'Category' },
          ]}
          onCreate={async (data) => createSkill(resumeId, data as any)}
          onUpdate={(entryId, data) => updateSkill(resumeId, entryId, data)}
          onDelete={(entryId) => deleteSkill(resumeId, entryId)}
        />

        <SectionEditor
          title="Certifications"
          entries={resume.certifications}
          fields={[
            { key: 'name', label: 'Certification *', required: true },
            { key: 'issuer', label: 'Issuer' },
            { key: 'date_obtained', label: 'Date (YYYY-MM)', type: 'month' },
            { key: 'url', label: 'URL', type: 'url' },
          ]}
          onCreate={async (data) => createCertification(resumeId, data as any)}
          onUpdate={(entryId, data) => updateCertification(resumeId, entryId, data)}
          onDelete={(entryId) => deleteCertification(resumeId, entryId)}
        />

        <div className="pb-8 text-center">
          <Link to={`/resumes/${resume.id}`} className="bg-gray-200 text-gray-700 rounded-md px-4 py-2 hover:bg-gray-300">
            View Resume
          </Link>
        </div>
      </div>
    </div>
  )
}

export default ResumeEditor
