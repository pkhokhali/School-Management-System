import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
  useTheme,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import MenuOpenIcon from '@mui/icons-material/MenuOpen'
import DashboardIcon from '@mui/icons-material/SpaceDashboardOutlined'
import PeopleIcon from '@mui/icons-material/PeopleOutline'
import SchoolIcon from '@mui/icons-material/SchoolOutlined'
import HowToRegIcon from '@mui/icons-material/HowToRegOutlined'
import EventNoteIcon from '@mui/icons-material/EventNoteOutlined'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonthOutlined'
import CampaignIcon from '@mui/icons-material/CampaignOutlined'
import PaymentsIcon from '@mui/icons-material/PaymentsOutlined'
import AssessmentIcon from '@mui/icons-material/AssessmentOutlined'
import BarChartIcon from '@mui/icons-material/BarChartOutlined'
import InsightsIcon from '@mui/icons-material/InsightsOutlined'
import SettingsIcon from '@mui/icons-material/SettingsOutlined'
import ManageAccountsIcon from '@mui/icons-material/ManageAccountsOutlined'
import DarkModeIcon from '@mui/icons-material/DarkModeOutlined'
import LightModeIcon from '@mui/icons-material/LightModeOutlined'
import LogoutIcon from '@mui/icons-material/LogoutOutlined'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import { useUiStore } from '../store/uiStore'
import { useFeatureStore } from '../store/featureStore'
import { usePermissions } from '../hooks/usePermissions'
import type { ModuleKey } from '../config/permissions'
import GlobalStudentSearch from '../components/GlobalStudentSearch'
import { instituteBrand } from '../theme/instituteBrand'

const DRAWER_WIDTH = 260

const navItems: {
  path: string
  label: string
  icon: React.ReactNode
  tKey?: string
  module: ModuleKey
  feature?: string
}[] = [
  { path: '/', label: 'Dashboard', icon: <DashboardIcon />, tKey: 'dashboard', module: 'dashboard' },
  { path: '/users', label: 'Users', icon: <ManageAccountsIcon />, module: 'users' },
  { path: '/students', label: 'Students', icon: <PeopleIcon />, module: 'students' },
  { path: '/courses', label: 'Courses & Academic', icon: <SchoolIcon />, module: 'courses' },
  { path: '/enrollment', label: 'Enrollment', icon: <HowToRegIcon />, module: 'enrollment' },
  { path: '/attendance', label: 'Attendance', icon: <EventNoteIcon />, module: 'attendance' },
  { path: '/calendar', label: 'Calendar', icon: <CalendarMonthIcon />, module: 'calendar' },
  { path: '/announcements', label: 'Announcements', icon: <CampaignIcon />, module: 'announcements' },
  { path: '/fees', label: 'Fees', icon: <PaymentsIcon />, module: 'fees' },
  { path: '/results', label: 'Results', icon: <AssessmentIcon />, module: 'results', feature: 'results_publishing' },
  { path: '/reports', label: 'BI Reports', icon: <BarChartIcon />, module: 'reports' },
  { path: '/analytics', label: 'At-risk analytics', icon: <InsightsIcon />, module: 'analytics', feature: 'predictive_analytics' },
  { path: '/settings', label: 'Settings', icon: <SettingsIcon />, module: 'settings' },
]

export default function DashboardLayout() {
  const [open, setOpen] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()
  const { t } = useTranslation()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const { darkMode, toggleDarkMode } = useUiStore()
  const isEnabled = useFeatureStore((s) => s.isEnabled)
  const { isSuperAdmin, canViewNav } = usePermissions()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const filteredNav = navItems.filter((item) => {
    if (!canViewNav(item.module)) return false
    if (isSuperAdmin) return true
    if (item.feature && !isEnabled(item.feature) && item.feature !== 'results_publishing') {
      return false
    }
    return true
  })

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path)

  const initials = user?.full_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'AD'

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (t) => t.zIndex.drawer + 1,
          bgcolor: darkMode ? instituteBrand.navy : 'background.paper',
          color: darkMode ? '#fff' : 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ gap: 1 }}>
          <IconButton onClick={() => setOpen(!open)} edge="start" aria-label="Toggle menu">
            {open ? <MenuOpenIcon /> : <MenuIcon />}
          </IconButton>
          <Typography
            variant="subtitle1"
            fontWeight={700}
            sx={{ display: { xs: 'none', md: 'block' }, fontFamily: '"Outfit", sans-serif' }}
          >
            Institute Admin
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <GlobalStudentSearch />
          <Tooltip title={darkMode ? 'Light mode' : 'Dark mode'}>
            <IconButton onClick={toggleDarkMode} size="small">
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
            <Box sx={{ display: { xs: 'none', sm: 'block' }, textAlign: 'right' }}>
              <Typography variant="body2" fontWeight={600}>
                {user?.full_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {isSuperAdmin ? 'Super Admin' : user?.role?.replace('_', ' ')}
              </Typography>
            </Box>
            <Avatar
              sx={{
                width: 40,
                height: 40,
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                fontWeight: 700,
                fontSize: '0.9rem',
              }}
            >
              {initials}
            </Avatar>
            <Tooltip title={t('logout')}>
              <IconButton color="error" onClick={handleLogout} aria-label={t('logout')}>
                <LogoutIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="persistent"
        open={open}
        sx={{
          width: open ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            top: 64,
            height: 'calc(100vh - 64px)',
            border: 'none',
            bgcolor: instituteBrand.navy,
            color: '#fff',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        <Box sx={{ px: 2, py: 2, flexShrink: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 42,
                height: 42,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${instituteBrand.indigo} 0%, #5b21b6 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 800,
                fontSize: '1.1rem',
                fontFamily: '"Outfit", sans-serif',
              }}
            >
              E
            </Box>
            <Box>
              <Typography variant="subtitle1" fontWeight={700} lineHeight={1.2} sx={{ color: '#fff' }}>
                EduInstitute
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                {isSuperAdmin ? 'Full access' : 'Admin portal'}
              </Typography>
            </Box>
          </Box>
        </Box>
        <Divider />
        <List sx={{ px: 1, py: 1, flex: 1, overflowY: 'auto' }}>
          {filteredNav.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ px: 2, py: 2 }}>
              Loading menu…
            </Typography>
          ) : (
            filteredNav.map((item) => (
              <ListItemButton
                key={item.path}
                selected={isActive(item.path)}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                <ListItemText
                  primary={item.tKey ? t(item.tKey) : item.label}
                  primaryTypographyProps={{ fontWeight: isActive(item.path) ? 600 : 500, fontSize: '0.9rem' }}
                />
              </ListItemButton>
            ))
          )}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minWidth: 0,
          p: { xs: 2, sm: 3 },
          mt: 8,
          transition: theme.transitions.create('margin', { duration: 225 }),
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
