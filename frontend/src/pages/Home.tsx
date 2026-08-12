import { useEffect, useState } from 'react'
import { getHealth } from '../api/health'
import type { HealthResponse } from '../types'

function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getHealth()
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message || 'Failed to connect to backend')
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">FixMyResume</h1>
        <p className="text-lg text-gray-600 mb-8">
          AI-powered resume analysis and job application tracking
        </p>

        <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Backend Status</h2>

          {loading && (
            <p className="text-gray-500">Checking backend connection...</p>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <p className="text-red-600">Error: {error}</p>
            </div>
          )}

          {health && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">API Status:</span>
                <span className={`font-medium ${health.status === 'ok' ? 'text-green-600' : 'text-red-600'}`}>
                  {health.status}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database:</span>
                <span className={`font-medium ${health.database === 'ok' ? 'text-green-600' : 'text-red-600'}`}>
                  {health.database}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Home