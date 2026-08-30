import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ResumeDetail from './pages/ResumeDetail'
import ResumeEditor from './pages/ResumeEditor'
import Analysis from './pages/Analysis'
import Resumes from './pages/Resumes'
import Tailor from './pages/Tailor'
import VersionsList from './pages/VersionsList'
import VersionDetail from './pages/VersionDetail'
import VersionCompare from './pages/VersionCompare'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Home />
      </ProtectedRoute>
    ),
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/resumes',
    element: (
      <ProtectedRoute>
        <Resumes />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumes/new',
    element: (
      <ProtectedRoute>
        <Resumes />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumes/:id',
    element: (
      <ProtectedRoute>
        <ResumeDetail />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumes/:id/analyze',
    element: (
      <ProtectedRoute>
        <Analysis />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumes/:id/edit',
    element: (
      <ProtectedRoute>
        <ResumeEditor />
      </ProtectedRoute>
    ),
  },
  {
    path: '/resumes/:id/tailor',
    element: (<ProtectedRoute><Tailor /></ProtectedRoute>),
  },
  {
    path: '/resumes/:id/versions',
    element: (<ProtectedRoute><VersionsList /></ProtectedRoute>),
  },
  {
    path: '/resumes/:id/versions/:versionId',
    element: (<ProtectedRoute><VersionDetail /></ProtectedRoute>),
  },
  {
    path: '/resumes/:id/versions/:versionId/compare',
    element: (<ProtectedRoute><VersionCompare /></ProtectedRoute>),
  },
])
