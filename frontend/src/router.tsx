import { createBrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ResumeDetail from './pages/ResumeDetail'
import ResumeEditor from './pages/ResumeEditor'
import Resumes from './pages/Resumes'

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
    path: '/resumes/:id/edit',
    element: (
      <ProtectedRoute>
        <ResumeEditor />
      </ProtectedRoute>
    ),
  },
])
