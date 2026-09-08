import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listApplications } from '../api/applications'
import { APPLICATION_STATUSES } from '../types/application'
import type { ApplicationSummary } from '../types/application'
import EmptyState from '../components/ui/EmptyState'

function Applications() {
  const [apps, setApps] = useState<ApplicationSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [sortBy, setSortBy] = useState('application_date')
  const [order, setOrder] = useState('desc')

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    listApplications({
      q: q || undefined,
      status: status || undefined,
      sort_by: sortBy,
      order,
    })
      .then(setApps)
      .catch((err: any) => setError(err?.response?.data?.detail || 'Failed to load applications'))
      .finally(() => setLoading(false))
  }, [q, status, sortBy, order])

  useEffect(() => {
    const t = setTimeout(load, 250)
    return () => clearTimeout(t)
  }, [load])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link to="/" className="text-blue-600 hover:underline text-sm">Home</Link>
            <h1 className="text-3xl font-bold text-gray-900 mt-1">Job Applications</h1>
          </div>
          <Link to="/applications/new" className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700">
            New Application
          </Link>
        </div>

        {error && <div className="bg-red-50 border border-red-200 rounded p-3 mb-4"><p className="text-red-600">{error}</p></div>}

        <div className="bg-white rounded-lg shadow-md p-4 mb-6 grid grid-cols-1 sm:grid-cols-4 gap-3">
          <input className="border border-gray-300 rounded-md px-3 py-2 text-sm" placeholder="Search company / title / location" value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="border border-gray-300 rounded-md px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            {APPLICATION_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="border border-gray-300 rounded-md px-3 py-2 text-sm" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="application_date">Applied date</option>
            <option value="updated_at">Last updated</option>
            <option value="created_at">Created</option>
            <option value="company">Company</option>
          </select>
          <select className="border border-gray-300 rounded-md px-3 py-2 text-sm" value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>

        {loading && <p className="text-gray-500 text-center py-12">Loading applications...</p>}

        {!loading && apps.length === 0 && (
          <EmptyState title="No applications yet" message="Track job applications to stay organized." actionLabel="New Application" />
        )}

        {!loading && apps.length > 0 && (
          <div className="space-y-3">
            {apps.map((a) => (
              <Link key={a.id} to={`/applications/${a.id}`} className="block bg-white rounded-lg shadow-md p-5 hover:shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{a.company} — {a.job_title}</p>
                    <p className="text-sm text-gray-500">Applied {new Date(a.application_date).toLocaleDateString()}{a.interview_date ? ` · Interview ${new Date(a.interview_date).toLocaleDateString()}` : ''}</p>
                  </div>
                  <span className="bg-blue-50 text-blue-700 rounded-full px-3 py-1 text-sm">{a.status}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Applications
