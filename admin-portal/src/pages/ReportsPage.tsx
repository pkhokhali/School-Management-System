import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Chip,
  Grid,
  Paper,
  Typography,
  alpha,
  useTheme,
} from '@mui/material'
import {
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
import PageHeader from '../components/PageHeader'
import PageTabs from '../components/PageTabs'
import StatCard from '../components/StatCard'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import { GridColDef } from '@mui/x-data-grid'
import PeopleAltOutlinedIcon from '@mui/icons-material/PeopleAltOutlined'
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined'
import HowToRegOutlinedIcon from '@mui/icons-material/HowToRegOutlined'
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined'
import PendingActionsOutlinedIcon from '@mui/icons-material/PendingActionsOutlined'
import api from '../api/client'

const PIE_COLORS = ['#3366ff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']

type BIReport = {
  generated_at?: string
  kpis?: Record<string, number>
  enrollment_by_status?: { status: string; count: number }[]
  enrollment_by_course?: { course_code: string; course_name: string; count: number }[]
  students_by_batch?: { batch_name: string; batch_code: string; count: number }[]
  students_by_department?: { department_name: string; department_code: string; count: number }[]
  course_capacity?: { course_code: string; course_name: string; enrolled: number; capacity: number; utilization_pct: number }[]
  payments_by_mode?: { mode: string; total: number; count: number }[]
  fee_collection_by_month?: { month: string; amount: number }[]
}

function formatNpr(n: number) {
  return new Intl.NumberFormat('en-NP', { style: 'currency', currency: 'NPR', maximumFractionDigits: 0 }).format(n)
}

function KpiGrid({ kpis }: { kpis: Record<string, number> }) {
  const cards = [
    { label: 'Total students', value: kpis.total_students, icon: <PeopleAltOutlinedIcon />, color: '#3366ff' },
    { label: 'Active courses', value: kpis.active_courses, icon: <SchoolOutlinedIcon />, color: '#8b5cf6' },
    { label: 'Approved enrollments', value: kpis.approved_enrollments, icon: <HowToRegOutlinedIcon />, color: '#10b981' },
    { label: 'Pending enrollments', value: kpis.pending_enrollments, icon: <PendingActionsOutlinedIcon />, color: '#f59e0b' },
    { label: 'Batches', value: kpis.total_batches, icon: <SchoolOutlinedIcon />, color: '#64748b' },
    { label: 'Departments', value: kpis.total_departments, icon: <SchoolOutlinedIcon />, color: '#0ea5e9' },
    { label: 'Teachers', value: kpis.total_teachers, icon: <PeopleAltOutlinedIcon />, color: '#6366f1' },
    { label: 'Fee collected (month)', value: formatNpr(Number(kpis.fee_collected_month || 0)), icon: <AccountBalanceWalletOutlinedIcon />, color: '#10b981' },
  ]
  return (
    <Grid container spacing={2.5} sx={{ mb: 2 }}>
      {cards.map((c) => (
        <Grid item xs={12} sm={6} md={3} key={c.label}>
          <StatCard label={c.label} value={c.value} icon={c.icon} color={c.color} />
        </Grid>
      ))}
    </Grid>
  )
}

function OverviewPanel({ report }: { report: BIReport }) {
  const theme = useTheme()
  const kpis = report.kpis || {}
  const enrollmentPie = useMemo(
    () => (report.enrollment_by_status || []).map((e) => ({
      name: e.status.charAt(0).toUpperCase() + e.status.slice(1),
      value: e.count,
    })),
    [report.enrollment_by_status],
  )
  const feeTrend = (report.fee_collection_by_month || []).map((r) => ({
    ...r,
    label: r.month,
    amount: Number(r.amount),
  }))

  return (
    <>
      <KpiGrid kpis={kpis} />
      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <ChartCard title="Fee collection trend" subtitle="Last 6 months (NPR)" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={feeTrend}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => formatNpr(v)} />
                <Bar dataKey="amount" name="Collected" fill={theme.palette.primary.main} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <ChartCard title="Enrollment status" subtitle="All applications" height={280}>
            {enrollmentPie.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={enrollmentPie} cx="50%" cy="50%" innerRadius={55} outerRadius={85} dataKey="value" paddingAngle={2}>
                    {enrollmentPie.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Typography color="text.secondary" align="center" sx={{ pt: 8 }}>No data</Typography>
            )}
          </ChartCard>
        </Grid>
      </Grid>
    </>
  )
}

function StudentsPanel({ report }: { report: BIReport }) {
  const batchCols: GridColDef[] = [
    { field: 'batch_code', headerName: 'Batch', width: 100 },
    { field: 'batch_name', headerName: 'Name', flex: 1 },
    { field: 'count', headerName: 'Students', width: 100 },
  ]
  const deptCols: GridColDef[] = [
    { field: 'department_code', headerName: 'Dept', width: 90 },
    { field: 'department_name', headerName: 'Department', flex: 1 },
    { field: 'count', headerName: 'Students', width: 100 },
  ]
  return (
    <Grid container spacing={2.5}>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Students by batch</Typography>
        <DataTable rows={report.students_by_batch || []} columns={batchCols} getRowId={(r) => `${r.batch_code}-${r.batch_name}`} autoHeight />
      </Grid>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Students by department</Typography>
        <DataTable rows={report.students_by_department || []} columns={deptCols} getRowId={(r) => `${r.department_code}-${r.department_name}`} autoHeight />
      </Grid>
    </Grid>
  )
}

function AcademicPanel({ report }: { report: BIReport }) {
  const courseCols: GridColDef[] = [
    { field: 'course_code', headerName: 'Code', width: 90 },
    { field: 'course_name', headerName: 'Program', flex: 1, minWidth: 160 },
    { field: 'enrolled', headerName: 'Enrolled', width: 90 },
    { field: 'capacity', headerName: 'Capacity', width: 90 },
    { field: 'utilization_pct', headerName: 'Fill %', width: 80 },
  ]
  const enrollCols: GridColDef[] = [
    { field: 'course_code', headerName: 'Code', width: 90 },
    { field: 'course_name', headerName: 'Program', flex: 1 },
    { field: 'count', headerName: 'Approved', width: 100 },
  ]
  return (
    <Grid container spacing={2.5}>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Enrollments by program</Typography>
        <DataTable rows={report.enrollment_by_course || []} columns={enrollCols} getRowId={(r) => r.course_code as string} autoHeight />
      </Grid>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Course capacity utilization</Typography>
        <DataTable rows={report.course_capacity || []} columns={courseCols} getRowId={(r) => r.course_code as string} autoHeight />
      </Grid>
    </Grid>
  )
}

function FinancePanel({ report }: { report: BIReport }) {
  const theme = useTheme()
  const kpis = report.kpis || {}
  const modeData = (report.payments_by_mode || []).map((r) => ({
    mode: r.mode,
    total: Number(r.total),
  }))
  const financeCards = [
    { label: 'Collected (all time)', value: formatNpr(Number(kpis.fee_collected_all_time || 0)) },
    { label: 'Collected (this month)', value: formatNpr(Number(kpis.fee_collected_month || 0)) },
    { label: 'Outstanding', value: formatNpr(Number(kpis.outstanding_fees || 0)) },
    { label: 'Overdue accounts', value: kpis.overdue_accounts ?? 0 },
  ]
  return (
    <>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {financeCards.map((c) => (
          <Grid item xs={12} sm={6} md={3} key={c.label}>
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
              <Typography variant="caption" color="text.secondary">{c.label}</Typography>
              <Typography variant="h5" fontWeight={700}>{c.value}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
      <ChartCard title="Collections by payment mode" subtitle="All time" height={280}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={modeData} layout="vertical" margin={{ left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="mode" tick={{ fontSize: 11 }} width={80} />
            <Tooltip formatter={(v: number) => formatNpr(v)} />
            <Bar dataKey="total" fill={theme.palette.success.main} radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </>
  )
}

function OperationsPanel({ report }: { report: BIReport }) {
  const navigate = useNavigate()
  const theme = useTheme()
  const kpis = report.kpis || {}
  const ops = [
    { label: 'Pending refund approvals', value: kpis.pending_refunds ?? 0, path: '/fees', hint: 'Fees → Refund workflow' },
    { label: 'Installments due (7 days)', value: kpis.installments_due_this_week ?? 0, path: '/fees', hint: 'Student ledger' },
    { label: 'Installment amount due', value: formatNpr(Number(kpis.installments_due_amount || 0)), path: '/fees', hint: 'Collection desk' },
    { label: 'Attendance present rate', value: `${kpis.attendance_present_rate ?? 0}%`, path: '/attendance', hint: 'Attendance module' },
    { label: 'Published announcements', value: kpis.published_announcements ?? 0, path: '/announcements', hint: 'Communications' },
    { label: 'Dropped enrollments', value: kpis.dropped_enrollments ?? 0, path: '/enrollment', hint: 'Enrollment review' },
  ]
  return (
    <Grid container spacing={2}>
      {ops.map((o) => (
        <Grid item xs={12} sm={6} md={4} key={o.label}>
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              borderRadius: 2,
              cursor: 'pointer',
              '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.04), borderColor: 'primary.main' },
            }}
            onClick={() => navigate(o.path)}
          >
            <Typography variant="caption" color="text.secondary">{o.label}</Typography>
            <Typography variant="h5" fontWeight={700}>{o.value}</Typography>
            <Chip size="small" label={o.hint} sx={{ mt: 1 }} variant="outlined" />
          </Paper>
        </Grid>
      ))}
    </Grid>
  )
}

export default function ReportsPage() {
  const [report, setReport] = useState<BIReport>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analytics/reports/')
      .then((r) => setReport(r.data))
      .finally(() => setLoading(false))
  }, [])

  const generated = report.generated_at
    ? new Date(report.generated_at).toLocaleString()
    : '—'

  return (
    <>
      <PageHeader
        title="BI Reports"
        subtitle={`Institute management analytics — generated ${generated}`}
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'BI Reports' }]}
      />
      {loading ? (
        <Typography color="text.secondary">Loading reports…</Typography>
      ) : (
        <PageTabs
          tabs={[
            { id: 'overview', label: 'Overview', panel: <OverviewPanel report={report} /> },
            { id: 'students', label: 'Students', panel: <StudentsPanel report={report} /> },
            { id: 'academic', label: 'Academic', panel: <AcademicPanel report={report} /> },
            { id: 'finance', label: 'Finance', panel: <FinancePanel report={report} /> },
            { id: 'operations', label: 'Operations', panel: <OperationsPanel report={report} /> },
          ]}
          defaultTab="overview"
        />
      )}
    </>
  )
}
