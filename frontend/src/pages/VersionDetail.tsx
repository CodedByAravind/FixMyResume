import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getVersion } from '../api/versions'
import type { VersionDetail } from '../types/resume_version'

export function SnapshotView({ snapshot, title }: { snapshot: any; title: string }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-5">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">{title}</h3>
      {snapshot.profile?.summary && <p className="text-sm text-gray-700 mb-2 whitespace-pre-wrap">{snapshot.profile.summary}</p>}
      {snapshot.skills?.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {snapshot.skills.map((s: any) => <span key={s.name} className="bg-blue-50 text-blue-700 rounded-full px-3 py-1 text-sm">{s.name}</span>)}
        </div>
      )}
      {snapshot.experience?.map((e: any) => (
        <p key={e.company + e.title} className="text-sm text-gray-700">{e.title} — {e.company}</p>
      ))}
      {snapshot.projects?.map((p: any) => (
        <p key={p.name} className="text-sm text-gray-700">{p.name}</p>
      ))}
    </div>
  )
}

function VersionDetailPage() {
  const { id, versionId } = useParams()
  const resumeId = Number(id)
  const vid = Number(versionId)
  const [detail, setDetail] = useState<VersionDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getVersion(resumeId, vid)
      .then(setDetail)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load version'))
      .finally(() => setLoading(false))
  }, [resumeId, vid])

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Loading...</div>
  if (error || !detail) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-red-600">{error || 'Not found'}</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <Link to={`/resumes/${resumeId}/versions`} className="text-blue-600 hover:underline text-sm">Back to versions</Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-1 mb-6">{detail.name}</h1>
        <p className="text-sm text-gray-500 mb-4">Source score {detail.analysis_score ?? 'n/a'} · Tailored score {detail.tailored_score ?? 'n/a'} · {new Date(detail.created_at).toLocaleDateString()}</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SnapshotView snapshot={detail.source} title="Source" />
          <SnapshotView snapshot={detail.tailored} title="Tailored" />
        </div>
      </div>
    </div>
  )
}

export default VersionDetailPage
