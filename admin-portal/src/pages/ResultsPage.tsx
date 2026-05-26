import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Step,
  StepConnector,
  StepLabel,
  Stepper,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  stepConnectorClasses,
  styled,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import SaveIcon from '@mui/icons-material/Save'
import PublishIcon from '@mui/icons-material/Publish'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import FormSection from '../components/FormSection'
import PageTabs from '../components/PageTabs'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'

type CourseOpt = { id: number; name: string; code: string }
type BatchOpt = { id: number; name: string }
type SubjectRow = {
  id: number
  course: number
  code: string
  name: string
  semester: number
  credit_hours: number
  max_internal: number
  max_external: number
  is_active: boolean
  course_name?: string
}

type MarkSheetSubject = { id: number; code: string; name: string; max_internal: number; max_external: number }
type MarkSheetStudent = {
  student_id: number
  student_name: string
  enrollment_number: string
  marks: Record<string, { internal_marks: number | null; external_marks: number | null; grade: string }>
}

const EXAM_TYPES = [
  { value: 'internal', label: 'Internal' },
  { value: 'mid_term', label: 'Mid Term' },
  { value: 'final', label: 'Final' },
]

const APPROVAL_STEPS = [
  { key: 'draft', label: 'Marks entered' },
  { key: 'teacher', label: 'Teacher review' },
  { key: 'hod', label: 'HOD approval' },
  { key: 'admin', label: 'Admin approval' },
  { key: 'published', label: 'Published' },
]

const ColorConnector = styled(StepConnector)(() => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: { top: 10 },
  [`& .${stepConnectorClasses.line}`]: { borderColor: '#bdbdbd' },
}))

type ExamSession = {
  id: number
  name: string
  exam_type: string
  term: string
  course_name: string
  subject_name?: string
  subject_code?: string
  marks_count: number
  is_published: boolean
  approval_id?: number | null
  approval_stage?: string | null
  approval_stage_label?: string
  next_stage?: string | null
}

function stageToStepIndex(stage: string | null | undefined, published: boolean): number {
  if (published) return 4
  if (!stage || stage === 'draft') return 0
  const idx = APPROVAL_STEPS.findIndex((s) => s.key === stage)
  return idx >= 0 ? idx : 0
}

function PublishApprovalPanel() {
  const user = useAuthStore((s) => s.user)
  const [courses, setCourses] = useState<CourseOpt[]>([])
  const [rows, setRows] = useState<ExamSession[]>([])
  const [filters, setFilters] = useState({ course: '', term: 'Fall 2025', exam_type: '', published: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
  }, [])

  const load = useCallback(() => {
    setLoading(true)
    const params: Record<string, string> = {}
    if (filters.course) params.course = filters.course
    if (filters.term) params.term = filters.term
    if (filters.exam_type) params.exam_type = filters.exam_type
    if (filters.published === 'false') params.is_published = 'false'
    if (filters.published === 'true') params.is_published = 'true'
    api.get('/results/exams/sessions/', { params })
      .then((r) => setRows(r.data.results || r.data))
      .catch(() => toast.error('Could not load exam sessions'))
      .finally(() => setLoading(false))
  }, [filters])

  useEffect(() => { load() }, [load])

  const submitApproval = async (examId: number) => {
    try {
      await api.post(`/results/exams/${examId}/submit-approval/`)
      toast.success('Submitted for approval')
      load()
    } catch {
      toast.error('Submit failed — ensure marks are entered')
    }
  }

  const advance = async (approvalId: number) => {
    try {
      await api.post(`/results/approvals/${approvalId}/advance/`)
      toast.success('Stage advanced')
      load()
    } catch {
      toast.error('Could not advance — check your role for this stage')
    }
  }

  const canAdvance = (stage: string | null | undefined) => {
    if (!stage || stage === 'draft') return false
    if (user?.role === 'super_admin') return stage !== 'published'
    if (user?.role === 'admin_staff') return ['hod', 'admin'].includes(stage || '')
    if (user?.role === 'teacher') return stage === 'teacher'
    return false
  }

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Workflow: enter marks → submit for approval → Teacher → HOD → Admin → Published.
        Students see marks only after Published.
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Program</InputLabel>
          <Select label="Program" value={filters.course} onChange={(e) => setFilters({ ...filters, course: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField size="small" label="Term" value={filters.term} onChange={(e) => setFilters({ ...filters, term: e.target.value })} />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Exam type</InputLabel>
          <Select label="Exam type" value={filters.exam_type} onChange={(e) => setFilters({ ...filters, exam_type: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            {EXAM_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Status</InputLabel>
          <Select label="Status" value={filters.published} onChange={(e) => setFilters({ ...filters, published: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="false">Pending publish</MenuItem>
            <MenuItem value="true">Published only</MenuItem>
          </Select>
        </FormControl>
        <Button variant="outlined" onClick={load} disabled={loading}>Refresh</Button>
      </Box>

      {rows.length === 0 && !loading && (
        <Typography color="text.secondary">No exam sessions match filters. Enter marks first, then submit for approval.</Typography>
      )}

      {rows.map((row) => {
        const activeStep = stageToStepIndex(row.approval_stage, row.is_published)
        return (
          <Paper key={row.id} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1, mb: 1 }}>
              <Box>
                <Typography fontWeight={700}>
                  {row.subject_code ? `${row.subject_code} — ${row.subject_name}` : row.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {row.course_name} · {EXAM_TYPES.find((t) => t.value === row.exam_type)?.label || row.exam_type} · {row.term}
                  {' · '}{row.marks_count} mark(s)
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                {row.is_published ? (
                  <Chip icon={<CheckCircleIcon />} label="Published" color="success" size="small" />
                ) : (
                  <Chip label={row.approval_stage_label || 'Draft'} size="small" color="warning" variant="outlined" />
                )}
                {!row.approval_id && !row.is_published && row.marks_count > 0 && (
                  <Button size="small" variant="contained" startIcon={<PublishIcon />} onClick={() => submitApproval(row.id)}>
                    Submit for approval
                  </Button>
                )}
                {row.approval_id && !row.is_published && canAdvance(row.approval_stage) && (
                  <Button size="small" variant="contained" color="secondary" onClick={() => advance(row.approval_id!)}>
                    Approve → {row.next_stage === 'published' ? 'Publish' : row.next_stage}
                  </Button>
                )}
              </Box>
            </Box>
            <Stepper activeStep={activeStep} alternativeLabel connector={<ColorConnector />} sx={{ mt: 1 }}>
              {APPROVAL_STEPS.map((s) => (
                <Step key={s.key} completed={activeStep > APPROVAL_STEPS.indexOf(s)}>
                  <StepLabel>{s.label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Paper>
        )
      })}
    </Box>
  )
}

function EnterMarksPanel({ canSave }: { canSave: boolean }) {
  const user = useAuthStore((s) => s.user)
  const [courses, setCourses] = useState<CourseOpt[]>([])
  const [batches, setBatches] = useState<BatchOpt[]>([])
  const [filters, setFilters] = useState({
    course: '',
    semester: '1',
    exam_type: 'mid_term',
    term: 'Fall 2025',
    batch: '',
  })
  const [subjects, setSubjects] = useState<MarkSheetSubject[]>([])
  const [students, setStudents] = useState<MarkSheetStudent[]>([])
  const [cellValues, setCellValues] = useState<Record<string, { internal: string; external: string }>>({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
    api.get('/courses/').then(async (r) => {
      let list: CourseOpt[] = r.data.results || r.data
      if (user?.role === 'teacher') {
        try {
          const a = await api.get('/courses/teacher-assignments/')
          const assigns = a.data.results || a.data
          const ids = new Set(assigns.map((x: { course: number }) => x.course))
          list = list.filter((c) => ids.has(c.id))
        } catch { /* keep full list if assignments unavailable */ }
      }
      setCourses(list)
    })
  }, [user?.role])

  const loadSheet = async () => {
    if (!filters.course) {
      toast.error('Select a program (course)')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.get('/results/mark-sheet/', {
        params: {
          course: filters.course,
          semester: filters.semester,
          exam_type: filters.exam_type,
          term: filters.term,
          ...(filters.batch ? { batch: filters.batch } : {}),
        },
      })
      setSubjects(data.subjects || [])
      setStudents(data.students || [])
      const cells: Record<string, { internal: string; external: string }> = {}
      for (const st of data.students || []) {
        for (const sub of data.subjects || []) {
          const m = st.marks?.[String(sub.id)]
          const key = `${st.student_id}-${sub.id}`
          cells[key] = {
            internal: m?.internal_marks != null ? String(m.internal_marks) : '',
            external: m?.external_marks != null ? String(m.external_marks) : '',
          }
        }
      }
      setCellValues(cells)
      if (!(data.subjects?.length)) toast.info('No subjects for this semester — add subjects in Program subjects tab')
      if (!(data.students?.length)) toast.info('No approved enrollments for this selection')
    } catch {
      toast.error('Could not load mark sheet')
    } finally {
      setLoading(false)
    }
  }

  const saveSheet = async () => {
    if (!filters.course) return
    const entries: { student_id: number; subject_id: number; internal_marks: number; external_marks: number }[] = []
    for (const st of students) {
      for (const sub of subjects) {
        const key = `${st.student_id}-${sub.id}`
        const cell = cellValues[key]
        if (!cell || (cell.internal === '' && cell.external === '')) continue
        entries.push({
          student_id: st.student_id,
          subject_id: sub.id,
          internal_marks: Number(cell.internal) || 0,
          external_marks: Number(cell.external) || 0,
        })
      }
    }
    if (!entries.length) {
      toast.error('Enter at least one mark')
      return
    }
    setSaving(true)
    try {
      const { data } = await api.post('/results/mark-sheet/', {
        course: Number(filters.course),
        semester: Number(filters.semester),
        exam_type: filters.exam_type,
        term: filters.term,
        batch: filters.batch ? Number(filters.batch) : null,
        entries,
      })
      if (data.errors?.length) {
        toast.warning(`Saved ${data.saved}; ${data.errors.length} row(s) skipped`)
      } else {
        toast.success(`Saved ${data.saved} mark(s)`)
      }
      loadSheet()
    } catch {
      toast.error('Save failed')
    } finally {
      setSaving(false)
    }
  }

  const setCell = (studentId: number, subjectId: number, field: 'internal' | 'external', value: string) => {
    const key = `${studentId}-${subjectId}`
    setCellValues((prev) => ({
      ...prev,
      [key]: { ...prev[key], internal: prev[key]?.internal ?? '', external: prev[key]?.external ?? '', [field]: value },
    }))
  }

  return (
    <Box>
      <FormSection title="Assessment context">
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
          <FormControl sx={{ minWidth: 220 }} size="small">
            <InputLabel>Program (course)</InputLabel>
            <Select
              label="Program (course)"
              value={filters.course}
              onChange={(e) => setFilters({ ...filters, course: e.target.value })}
            >
              {courses.map((c) => (
                <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            size="small"
            label="Semester"
            type="number"
            value={filters.semester}
            onChange={(e) => setFilters({ ...filters, semester: e.target.value })}
            sx={{ width: 100 }}
          />
          <FormControl sx={{ minWidth: 140 }} size="small">
            <InputLabel>Exam type</InputLabel>
            <Select
              label="Exam type"
              value={filters.exam_type}
              onChange={(e) => setFilters({ ...filters, exam_type: e.target.value })}
            >
              {EXAM_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
            </Select>
          </FormControl>
          <TextField
            size="small"
            label="Academic term"
            value={filters.term}
            onChange={(e) => setFilters({ ...filters, term: e.target.value })}
            sx={{ minWidth: 140 }}
          />
          <FormControl sx={{ minWidth: 160 }} size="small">
            <InputLabel>Batch (optional)</InputLabel>
            <Select
              label="Batch (optional)"
              value={filters.batch}
              onChange={(e) => setFilters({ ...filters, batch: e.target.value })}
            >
              <MenuItem value="">All enrolled</MenuItem>
              {batches.map((b) => <MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={loadSheet} disabled={loading}>
            {loading ? 'Loading…' : 'Load students'}
          </Button>
          {canSave && (
            <Button variant="contained" startIcon={<SaveIcon />} onClick={saveSheet} disabled={saving || !students.length}>
              Save marks
            </Button>
          )}
        </Box>
      </FormSection>

      {subjects.length > 0 && students.length > 0 && (
        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 520, overflow: 'auto' }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ minWidth: 180, bgcolor: 'background.paper' }}>Student</TableCell>
                {subjects.map((s) => (
                  <TableCell key={s.id} align="center" sx={{ minWidth: 140, bgcolor: 'background.paper' }}>
                    <Typography variant="caption" fontWeight={700} display="block">{s.code}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Int / Ext (max {s.max_internal}/{s.max_external})
                    </Typography>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {students.map((st) => (
                <TableRow key={st.student_id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>{st.student_name}</Typography>
                    <Typography variant="caption" color="text.secondary">{st.enrollment_number}</Typography>
                  </TableCell>
                  {subjects.map((sub) => {
                    const key = `${st.student_id}-${sub.id}`
                    const grade = st.marks?.[String(sub.id)]?.grade
                    return (
                      <TableCell key={sub.id} align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <TextField
                            size="small"
                            placeholder="Int"
                            type="number"
                            disabled={!canSave}
                            value={cellValues[key]?.internal ?? ''}
                            onChange={(e) => setCell(st.student_id, sub.id, 'internal', e.target.value)}
                            sx={{ width: 56 }}
                            inputProps={{ min: 0, max: sub.max_internal, step: 0.5 }}
                          />
                          <TextField
                            size="small"
                            placeholder="Ext"
                            type="number"
                            disabled={!canSave}
                            value={cellValues[key]?.external ?? ''}
                            onChange={(e) => setCell(st.student_id, sub.id, 'external', e.target.value)}
                            sx={{ width: 56 }}
                            inputProps={{ min: 0, max: sub.max_external, step: 0.5 }}
                          />
                        </Box>
                        {grade ? <Chip label={grade} size="small" sx={{ mt: 0.5 }} /> : null}
                      </TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

function MarksRegisterPanel() {
  const [rows, setRows] = useState([])
  const [courses, setCourses] = useState<CourseOpt[]>([])
  const [filters, setFilters] = useState({ course: '', exam_type: '', term: '' })

  const load = useCallback(() => {
    const params: Record<string, string | number> = {}
    if (filters.course) params.course = filters.course
    if (filters.exam_type) params.exam__exam_type = filters.exam_type
    if (filters.term) params.exam__term = filters.term
    api.get('/results/marks/', { params }).then((r) => setRows(r.data.results || r.data))
  }, [filters])

  useEffect(() => {
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'student_name', headerName: 'Student', width: 160 },
      { field: 'enrollment_number', headerName: 'ID', width: 110 },
      { field: 'course_name', headerName: 'Program', width: 140 },
      { field: 'subject_name', headerName: 'Subject', width: 130 },
      { field: 'exam_type', headerName: 'Type', width: 90 },
      { field: 'term', headerName: 'Term', width: 100 },
      { field: 'internal_marks', headerName: 'Internal', width: 80 },
      { field: 'external_marks', headerName: 'External', width: 80 },
      { field: 'grade', headerName: 'Grade', width: 70 },
      {
        field: 'is_published',
        headerName: 'Published',
        width: 100,
        renderCell: (p) => (
          <Chip label={p.value ? 'Yes' : 'No'} size="small" color={p.value ? 'success' : 'default'} variant="outlined" />
        ),
      },
    ],
    [],
  )

  return (
    <Box>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Program</InputLabel>
          <Select label="Program" value={filters.course} onChange={(e) => setFilters({ ...filters, course: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Exam type</InputLabel>
          <Select label="Exam type" value={filters.exam_type} onChange={(e) => setFilters({ ...filters, exam_type: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            {EXAM_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField size="small" label="Term" value={filters.term} onChange={(e) => setFilters({ ...filters, term: e.target.value })} />
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
    </Box>
  )
}

function ProgramSubjectsPanel({ canManage }: { canManage: boolean }) {
  const [rows, setRows] = useState<SubjectRow[]>([])
  const [courses, setCourses] = useState<CourseOpt[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<SubjectRow | null>(null)
  const [loading, setLoading] = useState(false)
  const [filterCourse, setFilterCourse] = useState('')
  const [form, setForm] = useState({
    course: '', code: '', name: '', semester: 1, credit_hours: 3,
    max_internal: 40, max_external: 60, is_active: true,
  })

  const load = useCallback(() => {
    const params: Record<string, string | number> = {}
    if (filterCourse) params.course = filterCourse
    api.get('/courses/subjects/', { params }).then((r) => setRows(r.data.results || r.data))
  }, [filterCourse])

  useEffect(() => {
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
    load()
  }, [load])

  const openForm = (row?: SubjectRow) => {
    setEditing(row || null)
    setForm(row ? {
      course: String(row.course),
      code: row.code,
      name: row.name,
      semester: row.semester,
      credit_hours: Number(row.credit_hours),
      max_internal: Number(row.max_internal),
      max_external: Number(row.max_external),
      is_active: row.is_active,
    } : {
      course: filterCourse || '',
      code: '',
      name: '',
      semester: 1,
      credit_hours: 3,
      max_internal: 40,
      max_external: 60,
      is_active: true,
    })
    setOpen(true)
  }

  const save = async () => {
    setLoading(true)
    try {
      const payload = {
        course: Number(form.course),
        code: form.code,
        name: form.name,
        semester: form.semester,
        credit_hours: form.credit_hours,
        max_internal: form.max_internal,
        max_external: form.max_external,
        is_active: form.is_active,
      }
      if (editing) await api.patch(`/courses/subjects/${editing.id}/`, payload)
      else await api.post('/courses/subjects/', payload)
      toast.success('Subject saved')
      setOpen(false)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'course_name', headerName: 'Program', flex: 1, minWidth: 140 },
      { field: 'code', headerName: 'Code', width: 90 },
      { field: 'name', headerName: 'Subject', flex: 1, minWidth: 140 },
      { field: 'semester', headerName: 'Sem', width: 60 },
      { field: 'max_internal', headerName: 'Max Int', width: 80 },
      { field: 'max_external', headerName: 'Max Ext', width: 80 },
      {
        field: 'is_active',
        headerName: 'Status',
        width: 90,
        renderCell: (p) => <Chip label={p.value ? 'Active' : 'Inactive'} size="small" color={p.value ? 'success' : 'default'} />,
      },
      ...(canManage ? buildActionColumns({ onEdit: openForm, canEdit: true, canView: false, canDelete: false }) : []),
    ],
    [canManage],
  )

  return (
    <Box>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2, alignItems: 'center' }}>
        <FormControl size="small" sx={{ minWidth: 220 }}>
          <InputLabel>Filter by program</InputLabel>
          <Select label="Filter by program" value={filterCourse} onChange={(e) => setFilterCourse(e.target.value)}>
            <MenuItem value="">All programs</MenuItem>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.name}</MenuItem>)}
          </Select>
        </FormControl>
        {canManage && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => openForm()}>
            Add subject
          </Button>
        )}
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} autoHeight />
      <FormDialog open={open} title={editing ? 'Edit subject' : 'Add subject'} onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Program</InputLabel>
          <Select label="Program" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} required>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Subject code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
        <TextField fullWidth margin="normal" label="Subject name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Semester" type="number" value={form.semester} onChange={(e) => setForm({ ...form, semester: Number(e.target.value) })} />
        <TextField fullWidth margin="normal" label="Credit hours" type="number" value={form.credit_hours} onChange={(e) => setForm({ ...form, credit_hours: Number(e.target.value) })} />
        <TextField fullWidth margin="normal" label="Max internal marks" type="number" value={form.max_internal} onChange={(e) => setForm({ ...form, max_internal: Number(e.target.value) })} />
        <TextField fullWidth margin="normal" label="Max external marks" type="number" value={form.max_external} onChange={(e) => setForm({ ...form, max_external: Number(e.target.value) })} />
        <Box sx={{ mt: 1 }}>
          <Switch checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active
        </Box>
      </FormDialog>
    </Box>
  )
}

export default function ResultsPage() {
  const { can, canCreate, isSuperAdmin, role } = usePermissions()
  const enabled = can('results', 'view')
  const canSave = canCreate('results')
  const canManageSubjects = isSuperAdmin || role === 'admin_staff'

  if (!enabled) {
    return (
      <>
        <PageHeader title="Results" subtitle="Marks and grade publishing" />
        <Typography color="text.secondary">Enable results_publishing in Settings to use this module.</Typography>
      </>
    )
  }

  return (
    <>
      <PageHeader
        title="Results"
        subtitle="Subject-wise marks per student program enrollment"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Results' }]}
      />
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Select the student&apos;s program, semester, and exam type. Enter internal and external marks for each subject.
        Super Admin, Admin Staff, and assigned Teachers can record marks.
      </Typography>
      <PageTabs
        tabs={[
          { id: 'enter', label: 'Enter marks', panel: <EnterMarksPanel canSave={canSave} /> },
          { id: 'publish', label: 'Publish & approval', panel: <PublishApprovalPanel /> },
          { id: 'register', label: 'Marks register', panel: <MarksRegisterPanel /> },
          ...(canManageSubjects
            ? [{ id: 'subjects', label: 'Program subjects', panel: <ProgramSubjectsPanel canManage={canManageSubjects} /> }]
            : []),
        ]}
      />
    </>
  )
}
