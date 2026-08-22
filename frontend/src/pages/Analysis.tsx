import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { analyzeResume } from '../api/analysis'
import { getResume } from '../api/resumes'
import type { AnalysisResult } from '../types/analysis'
import type { Resume } from '../types/resume'

function Analysis() {
  const { id } = useParams<{ id: string }>()
  const resumeId = Number(id)
  const [resume, setResume] = useState<Resume | null>(null)
  const [jd, setJd] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loadingResume, setLoadingResume] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getResume(resumeId)
      .then(setResume)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load resume'))
      .finally(() => setLoadingResume(false))
  }, [id])

  const handleAnalyze = async () => {
    if (jd.trim().length === 0) {
      setError('Please paste a job description first.')
      return
    }
    setError(null)
    setResult(null)
    setAnalyzing(true)
    try {
      const r = await analyzeResume(resumeId, jd)
      setResult(r)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (loadingResume) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  }

  if (error && !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-600">{error}</p>
          <Link to="/resumes" className="text-blue-600 hover:underline text-sm mt-2 inline-block">Back to resumes</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <Link to={`/resumes/${resume?.id}`} className="text-blue-600 hover:underline text-sm">View resume</Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-1">Analyze Against Job</h1>
          <p className="text-gray-600">Resume: {resume?.title}</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
          <textarea
            rows={10}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Paste the job description here..."
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            maxLength={20000}
          />
          <div className="mt-4">
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="bg-blue-600 text-white rounded-md px-5 py-2 hover:bg-blue-700 disabled:opacity-50"
            >
              {analyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {result && <AnalysisResults result={result} />}
      </div>
    </div>
  )
}

function AnalysisResults({ result }: { result: AnalysisResult }) {
  const barClass =
    result.score >= 75 ? 'bg-green-600' : result.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-semibold text-gray-800">Match Score</h2>
          <span className="text-4xl font-bold text-gray-900">{result.score}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div className={`${barClass} h-4 rounded-full`} style={{ width: `${result.score}%` }} />
        </div>
        <p className="text-gray-600">{result.summary}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Matched Skills">
          {result.matched_skills.length === 0 ? (
            <p className="text-gray-500 text-sm">No matched skills found.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {result.matched_skills.map((s) => (
                <span key={s.name} className="bg-green-100 text-green-800 rounded-full px-3 py-1 text-sm">{s.name}</span>
              ))}
            </div>
          )}
        </Card>
        <Card title="Missing Skills">
          {result.missing_skills.length === 0 ? (
            <p className="text-gray-500 text-sm">No missing skills. Great!</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {result.missing_skills.map((s) => (
                <span key={s.name} className="bg-red-100 text-red-700 rounded-full px-3 py-1 text-sm">{s.name}</span>
              ))}
            </div>
          )}
        </Card>
        <Card title="Job Keywords">
          <div className="flex flex-wrap gap-2">
            {result.job_keywords.map((k) => (
              <span key={k} className="bg-gray-100 text-gray-700 rounded-full px-3 py-1 text-sm">{k}</span>
            ))}
          </div>
        </Card>
        <Card title="Matched Keywords">
          {result.matched_keywords.length === 0 ? (
            <p className="text-gray-500 text-sm">None matched.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {result.matched_keywords.map((k) => (
                <span key={k} className="bg-blue-100 text-blue-700 rounded-full px-3 py-1 text-sm">{k}</span>
              ))}
            </div>
          )}
        </Card>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-3">Recommendations</h2>
        <ul className="list-disc pl-5 space-y-2">
          {result.recommendations.map((rec, i) => (
            <li key={i} className="text-gray-700">{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">{title}</h2>
      {children}
    </div>
  )
}

export default Analysis
