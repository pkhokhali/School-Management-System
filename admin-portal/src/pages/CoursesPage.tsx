import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  Chip,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import FormSection from '../components/FormSection'
import DetailDrawer from '../components/DetailDrawer'
import PageTabs from '../components/PageTabs'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

const COURSE_TYPES = [
  { value: 'program', label: 'Degree / Program' },
  { value: 'short_term', label: 'Short Term' },
  { value: 'internship', label: 'Internship' },
]

const LEVELS = [
  { value: 'certificate', label: 'Certificate' },
  { value: 'diploma', label: 'Diploma' },
  { value: 'bachelor', label: 'Bachelor' },
  { value: 'master', label: 'Master' },
  { value: 'phd', label: 'PhD' },
]

const DELIVERY = [
  { value: 'on_campus', label: 'On Campus' },
  { value: 'online', label: 'Online' },
  { value: 'hybrid', label: 'Hybrid' },
]

const MATERIAL_TYPES = [
  { value: 'note', label: 'Note' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'recording', label: 'Recording' },
  { value: 'video', label: 'Video Link' },
]

const emptyCourseForm = () => ({
  name: '',
  course_type: 'program',
  department: '',
  level: 'bachelor',
  duration_months: 48,
  duration_years: 4,
  total_semesters: 8,
  credits: 120,
  fee: 0,
  max_enrollment: 60,
  delivery_mode: 'on_campus',
  description: '',
  learning_outcomes: '',
  is_active: true,
})

type CourseRow = Record<string, unknown>

function AcademicSetupPanel({ canManage }: { canManage: boolean }) {
  const [departments, setDepartments] = useState<CourseRow[]>([])
  const [years, setYears] = useState<CourseRow[]>([])
  const [shifts, setShifts] = useState<CourseRow[]>([])
  const [batches, setBatches] = useState<CourseRow[]>([])
  const [dlg, setDlg] = useState<'dept' | 'year' | 'shift' | 'batch' | null>(null)
  const [editing, setEditing] = useState<CourseRow | null>(null)
  const [loading, setLoading] = useState(false)
  const [deptForm, setDeptForm] = useState({ name: '', code: '' })
  const [yearForm, setYearForm] = useState({ name: '', start_date: '', end_date: '', is_current: false })
  const [shiftForm, setShiftForm] = useState({ name: '', start_time: '', end_time: '', is_active: true })
  const [batchForm, setBatchForm] = useState({ name: '', code: '', department: '', academic_year: '', shift: '', semester: 1 })

  const load = useCallback(() => {
    api.get('/students/departments/').then((r) => setDepartments(r.data.results || r.data))
    api.get('/students/academic-years/').then((r) => setYears(r.data.results || r.data))
    api.get('/students/shifts/').then((r) => setShifts(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
  }, [])

  const activeShifts = useMemo(
    () => shifts.filter((s) => s.is_active !== false),
    [shifts],
  )

  useEffect(() => { load() }, [load])

  const saveDept = async () => {
    setLoading(true)
    try {
      if (editing) await api.patch(`/students/departments/${editing.id}/`, deptForm)
      else await api.post('/students/departments/', deptForm)
      toast.success('Department saved')
      setDlg(null)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const saveYear = async () => {
    setLoading(true)
    try {
      if (editing) await api.patch(`/students/academic-years/${editing.id}/`, yearForm)
      else await api.post('/students/academic-years/', yearForm)
      toast.success('Academic year saved')
      setDlg(null)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const saveShift = async () => {
    setLoading(true)
    try {
      const payload = {
        name: shiftForm.name,
        start_time: shiftForm.start_time || null,
        end_time: shiftForm.end_time || null,
        is_active: shiftForm.is_active,
      }
      if (editing) await api.patch(`/students/shifts/${editing.id}/`, payload)
      else await api.post('/students/shifts/', payload)
      toast.success('Shift saved')
      setDlg(null)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const deactivateShift = async (row: CourseRow) => {
    if (!window.confirm(`Deactivate shift "${row.name}"?`)) return
    try {
      await api.patch(`/students/shifts/${row.id}/`, { is_active: false })
      toast.success('Shift deactivated')
      load()
    } catch {
      toast.error('Deactivate failed')
    }
  }

  const saveBatch = async () => {
    setLoading(true)
    try {
      const payload = {
        ...batchForm,
        department: Number(batchForm.department),
        academic_year: Number(batchForm.academic_year),
        shift: batchForm.shift ? Number(batchForm.shift) : null,
        semester: Number(batchForm.semester),
      }
      if (editing) await api.patch(`/students/batches/${editing.id}/`, payload)
      else await api.post('/students/batches/', payload)
      toast.success('Batch saved')
      setDlg(null)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const deptCols: GridColDef[] = [
    { field: 'code', headerName: 'Code', width: 100 },
    { field: 'name', headerName: 'Department', flex: 1 },
    ...buildActionColumns({
      canEdit: canManage,
      onEdit: (row) => {
        setEditing(row)
        setDeptForm({ name: row.name as string, code: row.code as string })
        setDlg('dept')
      },
    }),
  ]

  const yearCols: GridColDef[] = [
    { field: 'name', headerName: 'Year', width: 140 },
    { field: 'start_date', headerName: 'Start', width: 120 },
    { field: 'end_date', headerName: 'End', width: 120 },
    {
      field: 'is_current',
      headerName: 'Current',
      width: 100,
      renderCell: (p) => (p.value ? <Chip label="Current" size="small" color="primary" /> : null),
    },
    ...buildActionColumns({
      canEdit: canManage,
      onEdit: (row) => {
        setEditing(row)
        setYearForm({
          name: row.name as string,
          start_date: row.start_date as string,
          end_date: row.end_date as string,
          is_current: row.is_current as boolean,
        })
        setDlg('year')
      },
    }),
  ]

  const shiftCols: GridColDef[] = [
    { field: 'name', headerName: 'Shift', flex: 1, minWidth: 100 },
    { field: 'timing_label', headerName: 'Timing', width: 120 },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 90,
      renderCell: (p) => (
        <Chip
          label={p.value ? 'Active' : 'Inactive'}
          size="small"
          color={p.value ? 'success' : 'default'}
          variant="outlined"
        />
      ),
    },
    ...buildActionColumns({
      canEdit: canManage,
      canDelete: canManage,
      onEdit: (row) => {
        setEditing(row)
        setShiftForm({
          name: row.name as string,
          start_time: (row.start_time as string)?.slice(0, 5) || '',
          end_time: (row.end_time as string)?.slice(0, 5) || '',
          is_active: row.is_active !== false,
        })
        setDlg('shift')
      },
      onDelete: deactivateShift,
    }),
  ]

  const batchCols: GridColDef[] = [
    { field: 'code', headerName: 'Code', width: 90 },
    { field: 'name', headerName: 'Batch', flex: 1 },
    { field: 'department_name', headerName: 'Department', width: 120 },
    { field: 'shift_name', headerName: 'Shift', width: 100 },
    { field: 'academic_year_name', headerName: 'Year', width: 100 },
    { field: 'semester', headerName: 'Sem', width: 60 },
    ...buildActionColumns({
      canEdit: canManage,
      onEdit: (row) => {
        setEditing(row)
        setBatchForm({
          name: row.name as string,
          code: row.code as string,
          department: String(row.department || ''),
          academic_year: String(row.academic_year || ''),
          shift: String(row.shift || ''),
          semester: row.semester as number,
        })
        setDlg('batch')
      },
    }),
  ]

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Configure departments, academic years, shifts, and batches before assigning students and courses.
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight={700}>Departments</Typography>
            {canManage && (
              <Button size="small" onClick={() => { setEditing(null); setDeptForm({ name: '', code: '' }); setDlg('dept') }}>Add</Button>
            )}
          </Box>
          <DataTable rows={departments} columns={deptCols} getRowId={(r) => r.id} autoHeight />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight={700}>Academic years</Typography>
            {canManage && (
              <Button size="small" onClick={() => { setEditing(null); setYearForm({ name: '', start_date: '', end_date: '', is_current: false }); setDlg('year') }}>Add</Button>
            )}
          </Box>
          <DataTable rows={years} columns={yearCols} getRowId={(r) => r.id} autoHeight />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight={700}>Shifts</Typography>
            {canManage && (
              <Button
                size="small"
                onClick={() => {
                  setEditing(null)
                  setShiftForm({ name: '', start_time: '', end_time: '', is_active: true })
                  setDlg('shift')
                }}
              >
                Add
              </Button>
            )}
          </Box>
          <DataTable rows={shifts} columns={shiftCols} getRowId={(r) => r.id} autoHeight />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight={700}>Batches</Typography>
            {canManage && (
              <Button
                size="small"
                onClick={() => {
                  setEditing(null)
                  setBatchForm({ name: '', code: '', department: '', academic_year: '', shift: '', semester: 1 })
                  setDlg('batch')
                }}
              >
                Add
              </Button>
            )}
          </Box>
          <DataTable rows={batches} columns={batchCols} getRowId={(r) => r.id} autoHeight />
        </Grid>
      </Grid>

      <FormDialog open={dlg === 'dept'} title={editing ? 'Edit department' : 'Add department'} onClose={() => setDlg(null)} onSubmit={saveDept} loading={loading}>
        <TextField fullWidth margin="normal" label="Name" value={deptForm.name} onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Code" value={deptForm.code} onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value })} />
      </FormDialog>
      <FormDialog open={dlg === 'year'} title={editing ? 'Edit academic year' : 'Add academic year'} onClose={() => setDlg(null)} onSubmit={saveYear} loading={loading}>
        <TextField fullWidth margin="normal" label="Name (e.g. 2025/26)" value={yearForm.name} onChange={(e) => setYearForm({ ...yearForm, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Start date" type="date" value={yearForm.start_date} onChange={(e) => setYearForm({ ...yearForm, start_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="End date" type="date" value={yearForm.end_date} onChange={(e) => setYearForm({ ...yearForm, end_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <FormControlLabel control={<Switch checked={yearForm.is_current} onChange={(e) => setYearForm({ ...yearForm, is_current: e.target.checked })} />} label="Current academic year" />
      </FormDialog>
      <FormDialog open={dlg === 'shift'} title={editing ? 'Edit shift' : 'Add shift'} onClose={() => setDlg(null)} onSubmit={saveShift} loading={loading}>
        <TextField fullWidth margin="normal" label="Name" value={shiftForm.name} onChange={(e) => setShiftForm({ ...shiftForm, name: e.target.value })} />
        <TextField
          fullWidth
          margin="normal"
          label="Start time"
          type="time"
          value={shiftForm.start_time}
          onChange={(e) => setShiftForm({ ...shiftForm, start_time: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          fullWidth
          margin="normal"
          label="End time"
          type="time"
          value={shiftForm.end_time}
          onChange={(e) => setShiftForm({ ...shiftForm, end_time: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <FormControlLabel
          control={<Switch checked={shiftForm.is_active} onChange={(e) => setShiftForm({ ...shiftForm, is_active: e.target.checked })} />}
          label="Active"
        />
      </FormDialog>
      <FormDialog open={dlg === 'batch'} title={editing ? 'Edit batch' : 'Add batch'} onClose={() => setDlg(null)} onSubmit={saveBatch} loading={loading}>
        <TextField fullWidth margin="normal" label="Batch name" value={batchForm.name} onChange={(e) => setBatchForm({ ...batchForm, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Code" value={batchForm.code} onChange={(e) => setBatchForm({ ...batchForm, code: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Department</InputLabel>
          <Select label="Department" value={batchForm.department} onChange={(e) => setBatchForm({ ...batchForm, department: e.target.value })}>
            {departments.map((d) => <MenuItem key={d.id as number} value={String(d.id)}>{d.name as string}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Academic year</InputLabel>
          <Select label="Academic year" value={batchForm.academic_year} onChange={(e) => setBatchForm({ ...batchForm, academic_year: e.target.value })}>
            {years.map((y) => <MenuItem key={y.id as number} value={String(y.id)}>{y.name as string}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Shift</InputLabel>
          <Select label="Shift" value={batchForm.shift} onChange={(e) => setBatchForm({ ...batchForm, shift: e.target.value })}>
            <MenuItem value="">None</MenuItem>
            {activeShifts.map((s) => (
              <MenuItem key={s.id as number} value={String(s.id)}>
                {s.name as string}
                {s.timing_label ? ` (${s.timing_label as string})` : ''}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Semester" type="number" value={batchForm.semester} onChange={(e) => setBatchForm({ ...batchForm, semester: Number(e.target.value) })} />
      </FormDialog>
    </Box>
  )
}

function CourseCatalogPanel() {
  const { canCreate, canEdit } = usePermissions()
  const manage = canCreate('courses') || canEdit('courses')
  const [rows, setRows] = useState<CourseRow[]>([])
  const [departments, setDepartments] = useState<{ id: number; name: string }[]>([])
  const [batches, setBatches] = useState<{ id: number; name: string }[]>([])
  const [teachers, setTeachers] = useState<{ id: number; full_name: string }[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<CourseRow | null>(null)
  const [form, setForm] = useState(emptyCourseForm())
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<CourseRow | null>(null)
  const [materialDlg, setMaterialDlg] = useState(false)
  const [teacherDlg, setTeacherDlg] = useState(false)
  const [matForm, setMatForm] = useState({ title: '', material_type: 'note', url: '' })
  const [teacherForm, setTeacherForm] = useState({ teacher: '', batch: '' })
  const [syllabusFile, setSyllabusFile] = useState<File | null>(null)

  const load = useCallback(() => {
    api.get('/courses/').then((r) => setRows(r.data.results || r.data))
    api.get('/students/departments/').then((r) => setDepartments(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
    api.get('/auth/users/', { params: { role: 'teacher' } }).then((r) => {
      const list = r.data.results || r.data
      setTeachers(list.map((u: { id: number; first_name: string; last_name: string }) => ({
        id: u.id,
        full_name: `${u.first_name || ''} ${u.last_name || ''}`.trim() || `Teacher #${u.id}`,
      })))
    }).catch(() => setTeachers([]))
  }, [])

  useEffect(() => { load() }, [load])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyCourseForm())
    setSyllabusFile(null)
    setOpen(true)
  }

  const openEdit = (row: CourseRow) => {
    setEditing(row)
    setSyllabusFile(null)
    setForm({
      name: row.name as string,
      course_type: (row.course_type as string) || 'program',
      department: row.department ? String(row.department) : '',
      level: (row.level as string) || 'bachelor',
      duration_months: row.duration_months as number,
      duration_years: Number(row.duration_years) || 4,
      total_semesters: row.total_semesters as number,
      credits: row.credits as number,
      fee: Number(row.fee) || 0,
      max_enrollment: row.max_enrollment as number,
      delivery_mode: (row.delivery_mode as string) || 'on_campus',
      description: (row.description as string) || '',
      learning_outcomes: (row.learning_outcomes as string) || '',
      is_active: row.is_active !== false,
    })
    setOpen(true)
  }

  const openDetail = async (row: CourseRow) => {
    try {
      const r = await api.get(`/courses/${row.id}/`)
      setDetail(r.data)
    } catch {
      setDetail(row)
    }
  }

  const save = async () => {
    setLoading(true)
    const { ...rest } = form as ReturnType<typeof emptyCourseForm> & { code?: string }
    const payload = {
      ...rest,
      department: form.department ? Number(form.department) : null,
      duration_years: Number(form.duration_years),
    }
    try {
      let courseId = editing?.id as number | undefined
      if (editing) {
        await api.patch(`/courses/${editing.id}/`, payload)
        courseId = editing.id as number
        toast.success('Course updated')
      } else {
        const res = await api.post('/courses/', payload)
        courseId = res.data.id
        toast.success(`Course created — code ${res.data.code}`)
      }
      if (syllabusFile && courseId) {
        const fd = new FormData()
        fd.append('syllabus_pdf', syllabusFile)
        await api.post(`/courses/${courseId}/upload-syllabus/`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      }
      setOpen(false)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const deactivate = async (row: CourseRow) => {
    if (!window.confirm(`Deactivate ${row.name}?`)) return
    await api.patch(`/courses/${row.id}/`, { is_active: false })
    toast.success('Course deactivated')
    load()
  }

  const addMaterial = async () => {
    if (!detail) return
    setLoading(true)
    try {
      await api.post('/courses/materials/', {
        course: detail.id,
        title: matForm.title,
        material_type: matForm.material_type,
        url: matForm.url,
      })
      toast.success('Material added')
      setMaterialDlg(false)
      openDetail({ id: detail.id })
      load()
    } catch {
      toast.error('Failed to add material')
    } finally {
      setLoading(false)
    }
  }

  const assignTeacher = async () => {
    if (!detail) return
    setLoading(true)
    try {
      await api.post('/courses/teacher-assignments/', {
        course: detail.id,
        teacher: Number(teacherForm.teacher),
        batch: teacherForm.batch ? Number(teacherForm.batch) : null,
      })
      toast.success('Faculty assigned')
      setTeacherDlg(false)
      openDetail({ id: detail.id })
    } catch {
      toast.error('Assignment failed — may already exist')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'code', headerName: 'Code', width: 110 },
      { field: 'name', headerName: 'Program / Course', flex: 1, minWidth: 180 },
      {
        field: 'course_type',
        headerName: 'Type',
        width: 110,
        valueFormatter: (v) => COURSE_TYPES.find((t) => t.value === v)?.label || String(v),
      },
      { field: 'department_name', headerName: 'Department', width: 130 },
      { field: 'level', headerName: 'Level', width: 100 },
      { field: 'duration_display', headerName: 'Duration', width: 160 },
      { field: 'credits', headerName: 'Credits', width: 80 },
      { field: 'fee', headerName: 'Fee (NPR)', width: 110 },
      { field: 'max_enrollment', headerName: 'Capacity', width: 90 },
      {
        field: 'is_active',
        headerName: 'Status',
        width: 100,
        renderCell: (p) => (
          <Chip label={p.value ? 'Active' : 'Inactive'} size="small" color={p.value ? 'success' : 'default'} variant="outlined" />
        ),
      },
      ...buildActionColumns({
        onView: openDetail,
        onEdit: openEdit,
        onDelete: deactivate,
        canView: true,
        canEdit: canEdit('courses'),
        canDelete: canEdit('courses'),
      }),
    ],
    [canEdit],
  )

  const detailMaterials = (detail?.materials as CourseRow[]) || []
  const detailTeachers = (detail?.teachers as CourseRow[]) || []
  const detailSyllabi = (detail?.syllabi as CourseRow[]) || []

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        {canCreate('courses') && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Add course / program
          </Button>
        )}
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />

      <FormDialog
        open={open}
        title={editing ? 'Edit course / program' : 'Add course / program'}
        onClose={() => setOpen(false)}
        onSubmit={save}
        loading={loading}
        maxWidth="md"
      >
        <FormSection title="Basic information">
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField fullWidth label="Course / program name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </Grid>
            {editing && (
              <Grid item xs={12} sm={4}>
                <TextField fullWidth label="Course code (auto)" value={(editing.code as string) || ''} disabled helperText="Assigned automatically on create" />
              </Grid>
            )}
            <Grid item xs={12} sm={editing ? 4 : 6}>
              <FormControl fullWidth>
                <InputLabel>Course type</InputLabel>
                <Select label="Course type" value={form.course_type} onChange={(e) => setForm({ ...form, course_type: e.target.value })}>
                  {COURSE_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select label="Department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })}>
                  <MenuItem value="">— None —</MenuItem>
                  {departments.map((d) => <MenuItem key={d.id} value={String(d.id)}>{d.name}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Level</InputLabel>
                <Select label="Level" value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })}>
                  {LEVELS.map((l) => <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Delivery mode</InputLabel>
                <Select label="Delivery mode" value={form.delivery_mode} onChange={(e) => setForm({ ...form, delivery_mode: e.target.value })}>
                  {DELIVERY.map((d) => <MenuItem key={d.value} value={d.value}>{d.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={<Switch checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />}
                label="Active (open for enrollment)"
              />
            </Grid>
          </Grid>
        </FormSection>

        <FormSection title="Duration & structure">
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <TextField fullWidth label="Years" type="number" inputProps={{ step: 0.5 }} value={form.duration_years} onChange={(e) => setForm({ ...form, duration_years: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={4}>
              <TextField fullWidth label="Months" type="number" value={form.duration_months} onChange={(e) => setForm({ ...form, duration_months: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={4}>
              <TextField fullWidth label="Semesters" type="number" value={form.total_semesters} onChange={(e) => setForm({ ...form, total_semesters: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Total credits" type="number" value={form.credits} onChange={(e) => setForm({ ...form, credits: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Max enrollment" type="number" value={form.max_enrollment} onChange={(e) => setForm({ ...form, max_enrollment: Number(e.target.value) })} />
            </Grid>
          </Grid>
        </FormSection>

        <FormSection title="Fees">
          <TextField fullWidth label="Program fee (NPR)" type="number" value={form.fee} onChange={(e) => setForm({ ...form, fee: Number(e.target.value) })} />
        </FormSection>

        <FormSection title="Description & outcomes">
          <TextField fullWidth label="Description" multiline rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} sx={{ mb: 2 }} />
          <TextField fullWidth label="Learning outcomes" multiline rows={3} value={form.learning_outcomes} onChange={(e) => setForm({ ...form, learning_outcomes: e.target.value })} placeholder="Skills and competencies graduates will gain" />
        </FormSection>
        <FormSection title="Syllabus (optional PDF)">
          <Button variant="outlined" component="label" sx={{ mb: 1 }}>
            {syllabusFile ? syllabusFile.name : 'Choose PDF'}
            <input type="file" hidden accept="application/pdf" onChange={(e) => setSyllabusFile(e.target.files?.[0] || null)} />
          </Button>
          {editing && (
            <Typography variant="caption" display="block" color="text.secondary">
              Current file on record — upload to replace
            </Typography>
          )}
        </FormSection>
      </FormDialog>

      <DetailDrawer
        open={!!detail}
        onClose={() => setDetail(null)}
        title={detail ? `${detail.code} — ${detail.name}` : ''}
        subtitle={detail?.department_name as string}
        width={560}
        actions={
          manage ? (
            <>
              <Button size="small" variant="outlined" onClick={() => { setMatForm({ title: '', material_type: 'note', url: '' }); setMaterialDlg(true) }}>Add material</Button>
              <Button size="small" variant="outlined" onClick={() => { setTeacherForm({ teacher: '', batch: '' }); setTeacherDlg(true) }}>Assign faculty</Button>
              <Button size="small" variant="contained" onClick={() => { if (detail) openEdit(detail); setDetail(null) }}>Edit course</Button>
            </>
          ) : undefined
        }
      >
        {detail && (
          <Box>
            <Grid container spacing={1} sx={{ mb: 2 }}>
              {([
                ['Level', detail.level],
                ['Delivery', detail.delivery_mode],
                ['Duration', `${detail.duration_years} yr · ${detail.duration_months} mo · ${detail.total_semesters} sem`],
                ['Credits', detail.credits],
                ['Fee', `NPR ${detail.fee}`],
                ['Capacity', detail.max_enrollment],
              ] as [string, unknown][]).map(([label, val]) => (
                <Grid item xs={6} key={label}>
                  <Typography variant="caption" color="text.secondary">{label}</Typography>
                  <Typography variant="body2" fontWeight={600}>{String(val ?? '—')}</Typography>
                </Grid>
              ))}
            </Grid>
            {detail.description ? (
              <>
                <Typography variant="subtitle2" fontWeight={700}>Description</Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>{String(detail.description)}</Typography>
              </>
            ) : null}
            {detail.learning_outcomes ? (
              <>
                <Typography variant="subtitle2" fontWeight={700}>Learning outcomes</Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>{String(detail.learning_outcomes)}</Typography>
              </>
            ) : null}
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Assigned faculty ({detailTeachers.length})</Typography>
            <List dense disablePadding>
              {detailTeachers.length === 0 && <Typography variant="body2" color="text.secondary">No faculty assigned yet.</Typography>}
              {detailTeachers.map((t) => (
                <ListItem key={t.id as number} disablePadding sx={{ py: 0.5 }}>
                  <ListItemText primary={t.teacher_name as string} secondary={t.batch_name ? `Batch: ${t.batch_name}` : 'All batches'} />
                </ListItem>
              ))}
            </List>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Syllabus ({detailSyllabi.length})</Typography>
            {detailSyllabi.length === 0 ? (
              <Typography variant="body2" color="text.secondary">Upload syllabus via API or Django admin.</Typography>
            ) : (
              detailSyllabi.map((s) => <Typography key={s.id as number} variant="body2">• {s.title as string}</Typography>)
            )}
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Materials ({detailMaterials.length})</Typography>
            <List dense disablePadding>
              {detailMaterials.map((m) => (
                <ListItem key={m.id as number} disablePadding sx={{ py: 0.5 }}>
                  <ListItemText primary={m.title as string} secondary={m.material_type as string} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DetailDrawer>

      <FormDialog open={materialDlg} title="Add course material" onClose={() => setMaterialDlg(false)} onSubmit={addMaterial} loading={loading}>
        <TextField fullWidth margin="normal" label="Title" value={matForm.title} onChange={(e) => setMatForm({ ...matForm, title: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Type</InputLabel>
          <Select label="Type" value={matForm.material_type} onChange={(e) => setMatForm({ ...matForm, material_type: e.target.value })}>
            {MATERIAL_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="URL (for videos/links)" value={matForm.url} onChange={(e) => setMatForm({ ...matForm, url: e.target.value })} />
      </FormDialog>

      <FormDialog open={teacherDlg} title="Assign faculty" onClose={() => setTeacherDlg(false)} onSubmit={assignTeacher} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Teacher</InputLabel>
          <Select label="Teacher" value={teacherForm.teacher} onChange={(e) => setTeacherForm({ ...teacherForm, teacher: e.target.value })}>
            {teachers.map((t) => <MenuItem key={t.id} value={String(t.id)}>{t.full_name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Batch (optional)</InputLabel>
          <Select label="Batch (optional)" value={teacherForm.batch} onChange={(e) => setTeacherForm({ ...teacherForm, batch: e.target.value })}>
            <MenuItem value="">All batches</MenuItem>
            {batches.map((b) => <MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>)}
          </Select>
        </FormControl>
      </FormDialog>
    </>
  )
}

export default function CoursesPage() {
  const { canEdit } = usePermissions()
  const canManageAcademic = canEdit('students') || canEdit('courses')

  return (
    <>
      <PageHeader
        title="Courses & academic setup"
        subtitle="Program catalog, duration, fees, faculty, materials, departments, batches"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Courses' }]}
      />
      <PageTabs
        tabs={[
          { id: 'catalog', label: 'Course catalog', panel: <CourseCatalogPanel /> },
          { id: 'academic', label: 'Academic setup', panel: <AcademicSetupPanel canManage={canManageAcademic} /> },
        ]}
      />
    </>
  )
}
