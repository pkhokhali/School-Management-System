import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { useFeatureStore } from './store/featureStore'
import { SUPER_ADMIN_PERMISSIONS, isSuperAdminRole } from './config/permissions'
import api from './api/client'
import LoginPage from './pages/LoginPage'
import DashboardLayout from './routes/DashboardLayout'
import DashboardPage from './pages/DashboardPage'
import StudentsPage from './pages/StudentsPage'
import CoursesPage from './pages/CoursesPage'
import EnrollmentPage from './pages/EnrollmentPage'
import AttendancePage from './pages/AttendancePage'
import CalendarPage from './pages/CalendarPage'
import AnnouncementsPage from './pages/AnnouncementsPage'
import FeesPage from './pages/FeesPage'
import ResultsPage from './pages/ResultsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'
import UsersPage from './pages/UsersPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const fetchFeatures = useFeatureStore((s) => s.fetchFeatures)
  const user = useAuthStore((s) => s.user)
  const permissions = useAuthStore((s) => s.permissions)
  const setPermissions = useAuthStore((s) => s.setPermissions)

  useEffect(() => {
    fetchFeatures().catch(() => {})
  }, [fetchFeatures])

  useEffect(() => {
    if (!user) return
    if (isSuperAdminRole(user.role)) {
      setPermissions(SUPER_ADMIN_PERMISSIONS)
      return
    }
    if (!permissions) {
      api.get('/auth/permissions/').then((r) => setPermissions(r.data.permissions)).catch(() => {})
    }
  }, [user, permissions, setPermissions])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <DashboardLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="courses" element={<CoursesPage />} />
        <Route path="enrollment" element={<EnrollmentPage />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="fees" element={<FeesPage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
