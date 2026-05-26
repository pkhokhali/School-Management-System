import { useCallback, useEffect, useMemo, useState } from 'react'
import { Button, Chip, FormControl, InputLabel, MenuItem, Select, Stack, TextField } from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import DetailDrawer from '../components/DetailDrawer'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

type Row = Record<string, unknown>

export default function EnrollmentPage() {
  const { canCreate, canEdit } = usePermissions()
  const [rows, setRows] = useState<Row[]>([])
  const [students, setStudents] = useState<{ id: number; full_name: string }[]>([])
  const [courses, setCourses] = useState<{ id: number; name: string; code: string }[]>([])
  const [open, setOpen] = useState(false)
  const [detail, setDetail] = useState<Row | null>(null)
  const [dropDlg, setDropDlg] = useState<Row | null>(null)
  const [dropReason, setDropReason] = useState('')
  const [form, setForm] = useState({ student: '', course: '' })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/enrollment/').then((r) => setRows(r.data.results || r.data))
    api.get('/students/').then((r) => setStudents(r.data.results || r.data))
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const approve = async (id: number) => {
    await api.post(`/enrollment/${id}/approve/`)
    toast.success('Enrollment approved')
    load()
  }

  const reject = async (id: number) => {
    await api.post(`/enrollment/${id}/reject/`)
    toast.success('Enrollment rejected')
    load()
    setDetail(null)
  }

  const drop = async () => {
    if (!dropDlg) return
    setLoading(true)
    try {
      await api.post(`/enrollment/${dropDlg.id}/drop/`, { reason: dropReason })
      toast.success('Enrollment dropped')
      setDropDlg(null)
      setDetail(null)
      load()
    } catch {
      toast.error('Drop failed')
    } finally {
      setLoading(false)
    }
  }

  const openCreate = () => {
    setForm({ student: '', course: '' })
    setOpen(true)
  }

  const save = async () => {
    setLoading(true)
    try {
      await api.post('/enrollment/', {
        student: Number(form.student),
        course: Number(form.course),
        status: 'pending',
      })
      toast.success('Enrollment request created')
      setOpen(false)
      load()
    } catch {
      toast.error('Create failed — student may already be enrolled')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'student_enrollment_number', headerName: 'Student ID', width: 120 },
      { field: 'student_name', headerName: 'Student', width: 160 },
      { field: 'course_name', headerName: 'Course / program', flex: 1, minWidth: 160 },
      { field: 'course_code', headerName: 'Course code', width: 100 },
      {
        field: 'created_at',
        headerName: 'Applied',
        width: 110,
        valueFormatter: (v) => (v ? String(v).slice(0, 10) : ''),
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 130,
        renderCell: (params) => (
          <Chip
            label={params.value}
            size="small"
            color={
              params.value === 'approved' ? 'success'
                : params.value === 'pending' ? 'warning'
                  : params.value === 'rejected' ? 'error'
                    : 'default'
            }
            variant="outlined"
          />
        ),
      },
      ...buildActionColumns({
        onView: setDetail,
        canView: true,
        canEdit: false,
      }),
      {
        field: 'workflow',
        headerName: 'Actions',
        width: 220,
        renderCell: (params) => {
          if (!canEdit('enrollment')) return null
          const row = params.row as Row
          if (row.status === 'pending') {
            return (
              <Stack direction="row" spacing={0.5}>
                <Button size="small" variant="contained" onClick={() => approve(row.id as number)}>Approve</Button>
                <Button size="small" color="error" onClick={() => reject(row.id as number)}>Reject</Button>
              </Stack>
            )
          }
          if (row.status === 'approved') {
            return (
              <Button size="small" color="warning" onClick={() => { setDropDlg(row); setDropReason('') }}>Drop</Button>
            )
          }
          return null
        },
      },
    ],
    [canEdit],
  )

  const pending = rows.filter((r) => r.status === 'pending').length

  return (
    <>
      <PageHeader
        title="Enrollment"
        subtitle={`Approve, reject, or drop student enrollments in courses${pending ? ` · ${pending} pending` : ''}`}
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Enrollment' }]}
        action={canCreate('enrollment') ? <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>Add enrollment</Button> : undefined}
      />
      <DataTable
        rows={rows}
        columns={columns}
        getRowId={(r) => r.id}
        initialState={{ sorting: { sortModel: [{ field: 'created_at', sort: 'desc' }] } }}
      />
      <FormDialog open={open} title="Enroll student in course" onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Student</InputLabel>
          <Select label="Student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })}>
            {students.map((s) => <MenuItem key={s.id} value={String(s.id)}>{s.full_name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Course / program</InputLabel>
          <Select label="Course / program" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })}>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>)}
          </Select>
        </FormControl>
      </FormDialog>

      <DetailDrawer
        open={!!detail}
        onClose={() => setDetail(null)}
        title={detail?.student_name as string}
        subtitle={detail?.course_name as string}
        actions={
          canEdit('enrollment') && detail?.status === 'pending' ? (
            <>
              <Button size="small" variant="contained" onClick={() => approve(detail.id as number)}>Approve</Button>
              <Button size="small" color="error" onClick={() => reject(detail.id as number)}>Reject</Button>
            </>
          ) : undefined
        }
      >
        {detail && (
          <>
            <Chip label={detail.status as string} sx={{ mb: 2 }} />
            <p><strong>Student:</strong> {detail.student_name as string}</p>
            <p><strong>Course:</strong> {detail.course_name as string}</p>
            {detail.drop_reason && <p><strong>Drop reason:</strong> {detail.drop_reason as string}</p>}
          </>
        )}
      </DetailDrawer>

      <FormDialog open={!!dropDlg} title="Drop enrollment" onClose={() => setDropDlg(null)} onSubmit={drop} loading={loading} submitLabel="Confirm drop">
        <TextField fullWidth margin="normal" label="Reason" multiline rows={2} value={dropReason} onChange={(e) => setDropReason(e.target.value)} />
      </FormDialog>
    </>
  )
}
