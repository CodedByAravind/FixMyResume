import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { compareVersion } from '../api/versions'
import type { CompareResult } from '../types/resume_version'
import { SnapshotView } from './VersionDetail'

function VersionCompare() {
  const { id, versionId } = useParams()
  const resumeId = Number(id)
  const vid = Number(versionId)
  const [data, setData] = useState<CompareResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    compareVersion(resumeId, vid)
      .then(setData)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to compare'))
      .finally(() => setLoading(false))
  }, [resumeId, vid])

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  if (error || !data) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-red-600">{error || 'Not found'}</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <Link to={`/resumes/${resumeId}/versions`} className="text-blue-600 hover:underline text-sm">Back to versions</Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-1 mb-2">Compare: {data.version_name}</h1>
        <p className="text-sm text-gray-500 mb-4">Source score {data.analysis_score ?? 'n/a'} · Tailored score {data.tailored_score ?? 'n/a'}</p>
        <div className="mb-4">
          <span className="text-sm font-medium text-gray-600">Changed sections: </span>
          {data.changed_sections.length === 0 ? (
            <span className="text-sm text-gray-500">None</span>
          ) : (
            data.changed_sections.map((s) => <span key={s} className="inline-block bg-amber-100 text-amber-800 rounded-full px-3 py-1 text-xs ml-1">{s}</span>)
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SnapshotView snapshot={data.source} title="Source (original snapshot)" />
          <SnapshotView snapshot={data.tailored} title="Tailored" />
        </div>
      </div>
    </div>
  )
}

export default VersionCompare
