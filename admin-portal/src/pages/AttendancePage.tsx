import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material'
import FileDownloadIcon from '@mui/icons-material/FileDownload'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import PageTabs from '../components/PageTabs'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

type BatchOption = { id: number; name: string; shift?: number; shift_name?: string }
type CourseOption = { id: number; name: string }

type RecordRow = {
  id: number
  student_name: string
  enrollment_number: string
  date: string
  status: string
  source: string
  needs_review: boolean
  course_name?: string
  batch_name?: string
}

const today = () => new Date().toISOString().slice(0, 10)

function MarkClassPanel() {
  const [batches, setBatches] = useState<BatchOption[]>([])
  const [courses, setCourses] = useState<CourseOption[]>([])
  const [students, setStudents] = useState<{ id: number; user: { full_name: string }; enrollment_number: string }[]>([])
  const [form, setForm] = useState({
    date: today(),
    batch: '',
    course: '',
    period: '1',
  })
  const [marks, setMarks] = useState<Record<number, string>>({})
  const [saving, setSaving] = useState(false)
  const [holidayWarning, setHolidayWarning] = useState<string | null>(null)

  useEffect(() => {
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
  }, [])

  useEffect(() => {
    if (!form.batch) {
      setStudents([])
      return
    }
    api.get('/students/', { params: { batch: form.batch } }).then((r) => {
      const list = r.data.results || r.data
      setStudents(list)
      const initial: Record<number, string> = {}
      list.forEach((s: { id: number }) => { initial[s.id] = 'present' })
      setMarks(initial)
    }).catch(() => toast.error('Could not load students'))
  }, [form.batch])

  const submit = async () => {
    if (!form.batch || !form.course) {
      toast.error('Select batch and course')
      return
    }
    setSaving(true)
    setHolidayWarning(null)
    try {
      const res = await api.post('/attendance/records/bulk/', {
        date: form.date,
        batch: Number(form.batch),
        course: Number(form.course),
        period: Number(form.period),
        records: students.map((s) => ({
          student_id: s.id,
          status: marks[s.id] || 'absent',
        })),
      })
      if (res.data.warnings?.length) {
        setHolidayWarning(res.data.warnings.join(' '))
        toast.warning(res.data.warnings[0])
      } else {
        toast.success('Class attendance saved')
      }
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const selectedBatch = batches.find((b) => String(b.id) === form.batch)

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 2 }}>
        Mark attendance by <strong>date, batch, course, and period</strong>. The class register is created
        automatically — no separate session setup required.
      </Alert>
      {holidayWarning && <Alert severity="warning" sx={{ mb: 2 }}>{holidayWarning}</Alert>}
      <Grid container spacing={2} sx={{ maxWidth: 900, mb: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <TextField fullWidth label="Date" type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} InputLabelProps={{ shrink: true }} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Batch</InputLabel>
            <Select label="Batch" value={form.batch} onChange={(e) => setForm({ ...form, batch: e.target.value })}>
              {batches.map((b) => (
                <MenuItem key={b.id} value={String(b.id)}>
                  {b.name}{b.shift_name ? ` (${b.shift_name})` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Course</InputLabel>
            <Select label="Course" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })}>
              {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.name}</MenuItem>)}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Period</InputLabel>
            <Select label="Period" value={form.period} onChange={(e) => setForm({ ...form, period: e.target.value })}>
              {[1, 2, 3, 4, 5, 6].map((p) => <MenuItem key={p} value={String(p)}>Period {p}</MenuItem>)}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      {selectedBatch?.shift_name && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Shift: {selectedBatch.shift_name} (from batch)
        </Typography>
      )}
      {students.length > 0 && (
        <>
          {students.map((s) => (
            <Box key={s.id} sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 0.5 }}>
              <Typography sx={{ flex: 1 }}>{s.user?.full_name} ({s.enrollment_number})</Typography>
              <Select size="small" value={marks[s.id] || 'present'} onChange={(e) => setMarks({ ...marks, [s.id]: e.target.value })}>
                <MenuItem value="present">Present</MenuItem>
                <MenuItem value="absent">Absent</MenuItem>
                <MenuItem value="late">Late</MenuItem>
              </Select>
            </Box>
          ))}
          <Button sx={{ mt: 2 }} variant="contained" disabled={saving} onClick={submit}>
            Save class attendance
          </Button>
        </>
      )}
    </Box>
  )
}

function ReportsPanel() {
  const [from, setFrom] = useState(today())
  const [to, setTo] = useState(today())
  const [rows, setRows] = useState<Record<string, unknown>[]>([])

  const load = () => {
    api.get('/attendance/reports/students/', { params: { from, to } }).then((r) => setRows(r.data.rows || []))
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'student_name', headerName: 'Student', width: 160 },
      { field: 'enrollment_number', headerName: 'ID', width: 110 },
      { field: 'batch_name', headerName: 'Batch', width: 120 },
      { field: 'course_name', headerName: 'Course', flex: 1, minWidth: 140 },
      { field: 'present', headerName: 'Present', width: 80 },
      { field: 'late', headerName: 'Late', width: 70 },
      { field: 'absent', headerName: 'Absent', width: 80 },
      {
        field: 'attendance_pct',
        headerName: '%',
        width: 80,
        renderCell: (p) => <Chip label={`${p.value}%`} size="small" color={(p.value as number) >= 75 ? 'success' : 'warning'} />,
      },
    ],
    [],
  )

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Attendance percentage per student per course (for academic review).
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <TextField label="From" type="date" value={from} onChange={(e) => setFrom(e.target.value)} InputLabelProps={{ shrink: true }} />
        <TextField label="To" type="date" value={to} onChange={(e) => setTo(e.target.value)} InputLabelProps={{ shrink: true }} />
        <Button variant="contained" onClick={load}>Load report</Button>
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => `${r.student_id}-${r.course_id}`} />
    </Box>
  )
}

function PayrollPanel() {
  const [from, setFrom] = useState(() => {
    const d = new Date()
    d.setDate(1)
    return d.toISOString().slice(0, 10)
  })
  const [to, setTo] = useState(today())
  const [data, setData] = useState<{ students: Record<string, unknown>[]; teachers: Record<string, unknown>[] } | null>(null)
  const [exporting, setExporting] = useState(false)

  const load = () => {
    api.get('/attendance/payroll-summary/', { params: { from, to } }).then((r) => setData(r.data))
  }

  const markExported = async () => {
    setExporting(true)
    try {
      const res = await api.post('/attendance/payroll-summary/', { from_date: from, to_date: to })
      toast.success(`Marked ${res.data.marked_exported} records as exported to payroll`)
      load()
    } catch {
      toast.error('Export failed')
    } finally {
      setExporting(false)
    }
  }

  const studentCols: GridColDef[] = [
    { field: 'student_name', headerName: 'Student', width: 160 },
    { field: 'batch_name', headerName: 'Batch', width: 120 },
    { field: 'payroll_eligible', headerName: 'Eligible days', width: 110 },
    { field: 'pending_export', headerName: 'Pending export', width: 120 },
    { field: 'exported', headerName: 'Exported', width: 90 },
  ]

  const teacherCols: GridColDef[] = [
    { field: 'teacher_name', headerName: 'Teacher', width: 180 },
    { field: 'class_days', headerName: 'Class days taught', width: 140 },
  ]

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 2 }}>
        Payroll integration foundation: eligible student attendance days and teacher class-days with marked
        registers. Mark as exported after your payroll run consumes this data.
      </Alert>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <TextField label="From" type="date" value={from} onChange={(e) => setFrom(e.target.value)} InputLabelProps={{ shrink: true }} />
        <TextField label="To" type="date" value={to} onChange={(e) => setTo(e.target.value)} InputLabelProps={{ shrink: true }} />
        <Button variant="contained" onClick={load}>Load summary</Button>
        <Button variant="outlined" startIcon={<FileDownloadIcon />} disabled={exporting || !data} onClick={markExported}>
          Mark period exported
        </Button>
      </Box>
      {data && (
        <>
          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Students (scholarship / stipend eligibility)</Typography>
          <DataTable rows={data.students} columns={studentCols} getRowId={(r) => r.student_id as number} />
          <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>Teachers (class-days for payroll)</Typography>
          <DataTable rows={data.teachers} columns={teacherCols} getRowId={(r) => r.teacher_id as number} />
        </>
      )}
    </Box>
  )
}

function OfflineReviewPanel() {
  const [rows, setRows] = useState<RecordRow[]>([])

  const load = useCallback(() => {
    api.get('/attendance/records/', { params: { source: 'offline' } }).then((offline) => {
      const offlineRows: RecordRow[] = offline.data.results || offline.data
      api.get('/attendance/records/', { params: { needs_review: true } }).then((conflicts) => {
        const conflictRows: RecordRow[] = conflicts.data.results || conflicts.data
        const byId = new Map<number, RecordRow>()
        ;[...offlineRows, ...conflictRows].forEach((r) => byId.set(r.id, r))
        setRows([...byId.values()])
      })
    })
  }, [])

  useEffect(() => { load() }, [load])

  const resolve = async (id: number, status: string) => {
    await api.post(`/attendance/records/${id}/resolve_conflict/`, { status })
    toast.success('Record updated')
    load()
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'student_name', headerName: 'Student', width: 160 },
      { field: 'course_name', headerName: 'Course', width: 130 },
      { field: 'date', headerName: 'Date', width: 110 },
      { field: 'status', headerName: 'Status', width: 90 },
      { field: 'source', headerName: 'Source', width: 90 },
      {
        field: 'resolve',
        headerName: 'Resolve',
        width: 180,
        renderCell: (p) =>
          p.row.needs_review ? (
            <>
              <Button size="small" onClick={() => resolve(p.row.id, 'present')}>Present</Button>
              <Button size="small" onClick={() => resolve(p.row.id, 'absent')}>Absent</Button>
            </>
          ) : null,
      },
    ],
    [],
  )

  return (
    <>
      <Alert severity="warning" sx={{ mb: 2 }}>
        Review offline sync and conflicts before payroll export.
      </Alert>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
    </>
  )
}

function RegistersListPanel() {
  const [rows, setRows] = useState<Record<string, unknown>[]>([])
  const [date, setDate] = useState(today())

  useEffect(() => {
    api.get('/attendance/sessions/', { params: { date } }).then((r) => setRows(r.data.results || r.data))
  }, [date])

  const columns: GridColDef[] = [
    { field: 'date', headerName: 'Date', width: 110 },
    { field: 'batch_name', headerName: 'Batch', width: 130 },
    { field: 'course_name', headerName: 'Course', flex: 1 },
    { field: 'period', headerName: 'P', width: 50 },
    { field: 'shift_name', headerName: 'Shift', width: 100 },
    { field: 'marked_count', headerName: 'Marked', width: 80 },
    { field: 'teacher_name', headerName: 'Teacher', width: 130 },
  ]

  return (
    <Box>
      <TextField sx={{ mb: 2 }} label="Date" type="date" value={date} onChange={(e) => setDate(e.target.value)} InputLabelProps={{ shrink: true }} />
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id as number} />
    </Box>
  )
}

export default function AttendancePage() {
  const { canCreate } = usePermissions()

  return (
    <>
      <PageHeader
        title="Attendance"
        subtitle="Class registers by batch, course & period — reports and payroll export"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Attendance' }]}
      />
      <PageTabs
        tabs={[
          { id: 'mark', label: 'Mark class', panel: <MarkClassPanel /> },
          { id: 'registers', label: "Today's registers", panel: <RegistersListPanel /> },
          { id: 'reports', label: 'Reports', panel: <ReportsPanel /> },
          ...(canCreate('attendance') ? [{ id: 'payroll', label: 'Payroll export', panel: <PayrollPanel /> }] : []),
          { id: 'offline', label: 'Offline & conflicts', panel: <OfflineReviewPanel /> },
        ]}
      />
    </>
  )
}
