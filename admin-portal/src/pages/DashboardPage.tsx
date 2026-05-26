import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  Chip,
  Grid,
  LinearProgress,
  Paper,
  Skeleton,
  Typography,
  alpha,
  useTheme,
} from '@mui/material'
import PeopleAltOutlinedIcon from '@mui/icons-material/PeopleAltOutlined'
import PendingActionsOutlinedIcon from '@mui/icons-material/PendingActionsOutlined'
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
import AssignmentReturnOutlinedIcon from '@mui/icons-material/AssignmentReturnOutlined'
import CalendarMonthOutlinedIcon from '@mui/icons-material/CalendarMonthOutlined'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuthStore } from '../store/authStore'
import StatCard from '../components/StatCard'
import ChartCard from '../components/ChartCard'

const PIE_COLORS = ['#3366ff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']

type DashboardStats = {
  total_students?: number
  pending_enrollments?: number
  fee_collected?: number
  overdue_fees?: number
  pending_refunds?: number
  installments_due_this_week?: number
  installments_due_amount?: number
  enrollment_by_status?: { status: string; count: number }[]
}

function formatCurrency(n: number) {
  return new Intl.NumberFormat('en-NP', { style: 'currency', currency: 'NPR', maximumFractionDigits: 0 }).format(n)
}

function formatDateLabel(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}

export default function DashboardPage() {
  const theme = useTheme()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [stats, setStats] = useState<DashboardStats>({})
  const [trend, setTrend] = useState<{ date: string; present: number }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/analytics/dashboard/'),
      api.get('/analytics/attendance-trend/?days=7'),
    ])
      .then(([dash, trendRes]) => {
        setStats(dash.data)
        setTrend(
          (trendRes.data as { date: string; present: number }[]).map((t) => ({
            ...t,
            label: formatDateLabel(t.date),
          })),
        )
      })
      .finally(() => setLoading(false))
  }, [])

  const enrollmentPie = useMemo(
    () =>
      (stats.enrollment_by_status ?? []).map((e) => ({
        name: e.status.charAt(0).toUpperCase() + e.status.slice(1),
        value: e.count,
      })),
    [stats.enrollment_by_status],
  )

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
  const isLight = theme.palette.mode === 'light'
  const primary = theme.palette.primary.main

  const quickActions = [
    { label: 'Add student', path: '/students', color: primary },
    { label: 'Review enrollments', path: '/enrollment', color: '#10b981' },
    { label: 'Mark attendance', path: '/attendance', color: '#8b5cf6' },
    { label: 'New announcement', path: '/announcements', color: '#f59e0b' },
  ]

  if (loading) {
    return (
      <Box>
        <Skeleton variant="rounded" height={120} sx={{ mb: 3, borderRadius: 3 }} />
        <Grid container spacing={2.5}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rounded" height={120} sx={{ borderRadius: 3 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  return (
    <Box>
      <Paper
        elevation={0}
        sx={{
          mb: 3,
          p: { xs: 2.5, md: 3.5 },
          borderRadius: 3,
          background: isLight
            ? `linear-gradient(135deg, ${primary} 0%, #5b8def 45%, #8b5cf6 100%)`
            : `linear-gradient(135deg, ${alpha(primary, 0.9)} 0%, ${alpha('#8b5cf6', 0.85)} 100%)`,
          color: '#fff',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            width: 280,
            height: 280,
            borderRadius: '50%',
            background: alpha('#fff', 0.08),
            top: -80,
            right: -60,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            width: 160,
            height: 160,
            borderRadius: '50%',
            background: alpha('#fff', 0.06),
            bottom: -40,
            left: '30%',
          }}
        />
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Chip
            label="Institute overview"
            size="small"
            sx={{
              mb: 1.5,
              bgcolor: alpha('#fff', 0.2),
              color: '#fff',
              fontWeight: 600,
              backdropFilter: 'blur(8px)',
            }}
          />
          <Typography variant="h4" sx={{ color: '#fff', mb: 0.5 }}>
            {greeting}, {user?.first_name || user?.full_name?.split(' ')[0] || 'Admin'}
          </Typography>
          <Typography sx={{ opacity: 0.9, maxWidth: 480 }}>
            Here&apos;s what&apos;s happening at your institute today — students, enrollments, fees, and attendance at a glance.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1.5, mt: 2.5, flexWrap: 'wrap' }}>
            <Chip
              icon={<TrendingUpIcon sx={{ color: '#fff !important' }} />}
              label={`${stats.total_students ?? 0} active students`}
              sx={{ bgcolor: alpha('#fff', 0.15), color: '#fff', fontWeight: 500 }}
            />
            <Chip
              label={`${stats.pending_enrollments ?? 0} pending approvals`}
              sx={{ bgcolor: alpha('#fff', 0.15), color: '#fff', fontWeight: 500 }}
            />
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            label="Total students"
            value={stats.total_students ?? 0}
            icon={<PeopleAltOutlinedIcon />}
            color="#3366ff"
            trend="+ Active profiles"
            trendUp
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            label="Pending enrollments"
            value={stats.pending_enrollments ?? 0}
            icon={<PendingActionsOutlinedIcon />}
            color="#8b5cf6"
            trend={stats.pending_enrollments ? 'Needs review' : 'All clear'}
            trendUp={!stats.pending_enrollments}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            label="Fee collected"
            value={formatCurrency(Number(stats.fee_collected ?? 0))}
            icon={<AccountBalanceWalletOutlinedIcon />}
            color="#10b981"
            trend="Total received"
            trendUp
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            label="Overdue accounts"
            value={stats.overdue_fees ?? 0}
            icon={<WarningAmberOutlinedIcon />}
            color="#f59e0b"
            trend={stats.overdue_fees ? 'Follow up' : 'On track'}
            trendUp={!stats.overdue_fees}
          />
        </Grid>
      </Grid>

      {(stats.pending_refunds ?? 0) > 0 || (stats.installments_due_this_week ?? 0) > 0 ? (
        <Grid container spacing={2.5} sx={{ mb: 3 }}>
          {(stats.pending_refunds ?? 0) > 0 && (
            <Grid item xs={12} sm={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 3,
                  border: (t) => `1px solid ${alpha(t.palette.error.main, 0.25)}`,
                  bgcolor: (t) => alpha(t.palette.error.main, 0.05),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <AssignmentReturnOutlinedIcon color="error" />
                  <Box>
                    <Typography fontWeight={600}>{stats.pending_refunds} refund(s) pending approval</Typography>
                    <Typography variant="body2" color="text.secondary">Accountant action required</Typography>
                  </Box>
                </Box>
                <Button size="small" variant="outlined" color="error" onClick={() => navigate('/fees')}>
                  Review refunds
                </Button>
              </Paper>
            </Grid>
          )}
          {(stats.installments_due_this_week ?? 0) > 0 && (
            <Grid item xs={12} sm={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 3,
                  border: (t) => `1px solid ${alpha(t.palette.warning.main, 0.25)}`,
                  bgcolor: (t) => alpha(t.palette.warning.main, 0.05),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <CalendarMonthOutlinedIcon color="warning" />
                  <Box>
                    <Typography fontWeight={600}>
                      {stats.installments_due_this_week} installment(s) due this week
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      NPR {Number(stats.installments_due_amount ?? 0).toLocaleString()} expected
                    </Typography>
                  </Box>
                </Box>
                <Button size="small" variant="outlined" color="warning" onClick={() => navigate('/fees')}>
                  Open fees
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      ) : null}

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={8}>
          <ChartCard title="Attendance trend" subtitle="Daily present count — last 7 days" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="attendanceGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={primary} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={primary} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.08)} vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke={theme.palette.text.secondary} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke={theme.palette.text.secondary} />
                <Tooltip
                  contentStyle={{
                    borderRadius: 12,
                    border: `1px solid ${alpha(primary, 0.2)}`,
                    boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="present"
                  stroke={primary}
                  strokeWidth={2.5}
                  fill="url(#attendanceGrad)"
                  name="Present"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>
        <Grid item xs={12} lg={4}>
          <ChartCard title="Enrollment mix" subtitle="By status" height={280}>
            {enrollmentPie.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={enrollmentPie}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {enrollmentPie.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Typography color="text.secondary">No enrollment data yet</Typography>
              </Box>
            )}
          </ChartCard>
        </Grid>
      </Grid>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={5}>
          <Paper elevation={0} sx={{ p: 2.5, height: '100%', borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick actions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Jump to common tasks
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {quickActions.map((action) => (
                <Button
                  key={action.path}
                  variant="outlined"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate(action.path)}
                  sx={{
                    justifyContent: 'space-between',
                    py: 1.25,
                    borderColor: alpha(action.color, 0.35),
                    color: 'text.primary',
                    '&:hover': {
                      borderColor: action.color,
                      bgcolor: alpha(action.color, 0.06),
                    },
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={7}>
          <ChartCard title="Weekly activity" subtitle="Attendance volume by day" height={220}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trend} barSize={28} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.text.primary, 0.08)} vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="present" name="Present" radius={[8, 8, 0, 0]}>
                  {trend.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>
      </Grid>

      {(stats.pending_enrollments ?? 0) > 0 && (
        <Paper
          elevation={0}
          sx={{
            mt: 2.5,
            p: 2,
            borderRadius: 3,
            border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
            bgcolor: alpha(theme.palette.warning.main, 0.06),
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            flexWrap: 'wrap',
          }}
        >
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <Typography fontWeight={600}>
              {stats.pending_enrollments} enrollment{stats.pending_enrollments !== 1 ? 's' : ''} awaiting approval
            </Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min(100, (stats.pending_enrollments ?? 0) * 10)}
              sx={{ mt: 1, height: 6, borderRadius: 3 }}
            />
          </Box>
          <Button variant="contained" onClick={() => navigate('/enrollment')}>
            Review now
          </Button>
        </Paper>
      )}
    </Box>
  )
}
