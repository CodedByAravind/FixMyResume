import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { tailorResume } from '../api/versions'
import type { TailoredVersion } from '../types/resume_version'

function Tailor() {
  const { id } = useParams()
  const resumeId = Number(id)
  const [jd, setJd] = useState('')
  const [name, setName] = useState('')
  const [version, setVersion] = useState<TailoredVersion | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runTailor = async () => {
    if (!jd.trim()) {
      setError('Please paste a job description first.')
      return
    }
    setError(null)
    setVersion(null)
    setBusy(true)
    try {
      const v = await tailorResume(resumeId, { job_description: jd, name: name || undefined })
      setVersion(v)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Tailoring failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <Link to={`/resumes/${resumeId}/versions`} className="text-blue-600 hover:underline text-sm">Back to versions</Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-1">Tailor Resume</h1>
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded p-3"><p className="text-red-600">{error}</p></div>}

        <div className="bg-white rounded-lg shadow-md p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
          <textarea
            rows={8}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            maxLength={20000}
          />
          <input
            className="mt-3 w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            placeholder="Version name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button
            onClick={runTailor}
            disabled={busy}
            className="mt-4 bg-blue-600 text-white rounded-md px-5 py-2 hover:bg-blue-700 disabled:opacity-50"
          >
            {busy ? 'Tailoring...' : 'Tailor'}
          </button>
        </div>

        {version && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">Tailored version created</h2>
            <p className="text-sm text-gray-600 mb-2">Changed sections: {version.changed_sections.join(', ')}</p>
            <ul className="list-disc pl-5 mb-2">
              {version.recommendations.map((r, i) => <li key={i} className="text-gray-700">{r}</li>)}
            </ul>
            {version.warnings.map((w, i) => <p key={i} className="text-sm text-amber-600">{w}</p>)}
            <Link to={`/resumes/${resumeId}/versions/${version.id}`} className="inline-block mt-4 bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700">
              View version
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default Tailor
