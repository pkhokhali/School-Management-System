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
  Paper,
  Select,
  TextField,
  Typography,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import BeachAccessIcon from '@mui/icons-material/BeachAccess'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import PageTabs from '../components/PageTabs'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

const EVENT_TYPES = [
  { value: 'public_holiday', label: 'Public holiday', color: 'error' as const },
  { value: 'holiday', label: 'Institute holiday', color: 'warning' as const },
  { value: 'term_break', label: 'Term break', color: 'info' as const },
  { value: 'exam', label: 'Exam period', color: 'secondary' as const },
  { value: 'event', label: 'Academic / cultural event', color: 'primary' as const },
  { value: 'admission', label: 'Admission', color: 'success' as const },
  { value: 'meeting', label: 'Meeting / assembly', color: 'default' as const },
]

const HOLIDAY_TYPES = ['public_holiday', 'holiday', 'term_break']

type AcademicYear = { id: number; name: string; is_current: boolean; start_date: string; end_date: string }
type CalendarEvent = {
  id: number
  title: string
  event_type: string
  start_date: string
  end_date: string
  description: string
  academic_year: number | null
  academic_year_name?: string
}

const typeLabel = (v: string) => EVENT_TYPES.find((t) => t.value === v)?.label ?? v
const typeColor = (v: string) => EVENT_TYPES.find((t) => t.value === v)?.color ?? 'default'

const emptyEvent = (yearId: string) => ({
  title: '',
  event_type: 'event',
  start_date: new Date().toISOString().slice(0, 10),
  end_date: new Date().toISOString().slice(0, 10),
  description: '',
  academic_year: yearId,
})

function MonthCalendar({
  year,
  month,
  events,
  onPrev,
  onNext,
}: {
  year: number
  month: number
  events: CalendarEvent[]
  onPrev: () => void
  onNext: () => void
}) {
  const monthLabel = new Date(year, month - 1, 1).toLocaleString('default', { month: 'long', year: 'numeric' })
  const firstDow = new Date(year, month - 1, 1).getDay()
  const daysInMonth = new Date(year, month, 0).getDate()
  const cells: (number | null)[] = [...Array(firstDow).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)]

  const eventsOnDay = (day: number) => {
    const d = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    return events.filter((e) => e.start_date <= d && e.end_date >= d)
  }

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Button startIcon={<ChevronLeftIcon />} onClick={onPrev}>Previous</Button>
        <Typography variant="h6">{monthLabel}</Typography>
        <Button endIcon={<ChevronRightIcon />} onClick={onNext}>Next</Button>
      </Box>
      <Grid container spacing={0.5} sx={{ mb: 0.5 }}>
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
          <Grid item xs={12 / 7} key={d}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ pl: 0.5 }}>
              {d}
            </Typography>
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={0.5}>
        {cells.map((day, idx) => (
          <Grid item xs={12 / 7} key={idx}>
            <Box
              sx={{
                minHeight: 72,
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                p: 0.5,
                bgcolor: day ? 'background.paper' : 'action.hover',
              }}
            >
              {day && (
                <>
                  <Typography variant="caption" fontWeight={600}>{day}</Typography>
                  {eventsOnDay(day).slice(0, 2).map((e) => (
                    <Chip
                      key={e.id}
                      label={e.title}
                      size="small"
                      color={typeColor(e.event_type)}
                      sx={{ display: 'block', height: 18, fontSize: '0.65rem', mt: 0.25, maxWidth: '100%' }}
                    />
                  ))}
                  {eventsOnDay(day).length > 2 && (
                    <Typography variant="caption" color="text.secondary">+{eventsOnDay(day).length - 2}</Typography>
                  )}
                </>
              )}
            </Box>
          </Grid>
        ))}
      </Grid>
    </Paper>
  )
}

function CalendarMainPanel({ canManage }: { canManage: boolean }) {
  const [years, setYears] = useState<AcademicYear[]>([])
  const [yearId, setYearId] = useState('')
  const [viewYear, setViewYear] = useState(new Date().getFullYear())
  const [viewMonth, setViewMonth] = useState(new Date().getMonth() + 1)
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [summary, setSummary] = useState<{ working_days: number; holiday_days: number; total_days: number } | null>(null)
  const [filterType, setFilterType] = useState('')
  const [dlg, setDlg] = useState<'event' | 'holiday' | 'bulk' | null>(null)
  const [loading, setLoading] = useState(false)
  const [eventForm, setEventForm] = useState(emptyEvent(''))
  const [holidayForm, setHolidayForm] = useState({
    title: '',
    event_type: 'holiday',
    start_date: '',
    end_date: '',
    description: '',
    academic_year: '',
  })
  const [bulkFile, setBulkFile] = useState<File | null>(null)
  const [editing, setEditing] = useState<CalendarEvent | null>(null)

  const loadYears = useCallback(() => {
    api.get('/students/academic-years/').then((r) => {
      const list: AcademicYear[] = r.data.results || r.data
      setYears(list)
      const current = list.find((y) => y.is_current) ?? list[0]
      if (current && !yearId) {
        setYearId(String(current.id))
        setEventForm(emptyEvent(String(current.id)))
        setHolidayForm((f) => ({ ...f, academic_year: String(current.id) }))
      }
    })
  }, [yearId])

  const loadMonth = useCallback(() => {
    const params: Record<string, string | number> = { year: viewYear, month: viewMonth }
    if (yearId) params.academic_year = yearId
    api.get('/events/calendar/month/', { params }).then((r) => {
      setEvents(r.data.events)
      setSummary(r.data.summary)
    })
  }, [viewYear, viewMonth, yearId])

  useEffect(() => { loadYears() }, [loadYears])
  useEffect(() => { loadMonth() }, [loadMonth])

  const filteredEvents = useMemo(
    () => (filterType ? events.filter((e) => e.event_type === filterType) : events),
    [events, filterType],
  )

  const saveEvent = async () => {
    setLoading(true)
    try {
      const payload = {
        ...eventForm,
        academic_year: eventForm.academic_year ? Number(eventForm.academic_year) : null,
      }
      if (editing) await api.patch(`/events/${editing.id}/`, payload)
      else await api.post('/events/', payload)
      toast.success('Calendar entry saved')
      setDlg(null)
      setEditing(null)
      loadMonth()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const saveHolidayRange = async () => {
    setLoading(true)
    try {
      await api.post('/events/mark-holiday-range/', {
        ...holidayForm,
        academic_year: holidayForm.academic_year ? Number(holidayForm.academic_year) : null,
      })
      toast.success('Holiday / break marked')
      setDlg(null)
      loadMonth()
    } catch {
      toast.error('Could not mark holiday range')
    } finally {
      setLoading(false)
    }
  }

  const uploadBulk = async () => {
    if (!bulkFile) {
      toast.error('Choose a CSV file')
      return
    }
    setLoading(true)
    try {
      const form = new FormData()
      form.append('file', bulkFile)
      if (yearId) form.append('academic_year', yearId)
      const res = await api.post('/events/bulk-upload/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const { created, skipped, errors } = res.data
      toast.success(`Imported ${created.length}, skipped ${skipped.length}`)
      if (errors?.length) toast.warning(errors.slice(0, 3).join('; '))
      setDlg(null)
      setBulkFile(null)
      loadMonth()
    } catch {
      toast.error('Bulk upload failed')
    } finally {
      setLoading(false)
    }
  }

  const deleteEvent = async (row: CalendarEvent) => {
    if (!window.confirm(`Delete "${row.title}"?`)) return
    await api.delete(`/events/${row.id}/`)
    toast.success('Deleted')
    loadMonth()
  }

  const shiftMonth = (delta: number) => {
    let m = viewMonth + delta
    let y = viewYear
    if (m < 1) { m = 12; y -= 1 }
    if (m > 12) { m = 1; y += 1 }
    setViewMonth(m)
    setViewYear(y)
  }

  const columns: GridColDef[] = [
    { field: 'title', headerName: 'Title', flex: 1, minWidth: 160 },
    {
      field: 'event_type',
      headerName: 'Type',
      width: 150,
      renderCell: (p) => <Chip label={typeLabel(p.value as string)} size="small" color={typeColor(p.value as string)} />,
    },
    { field: 'start_date', headerName: 'From', width: 110 },
    { field: 'end_date', headerName: 'To', width: 110 },
    { field: 'academic_year_name', headerName: 'Academic year', width: 130 },
    ...buildActionColumns({
      canEdit: canManage,
      canDelete: canManage,
      onEdit: (row) => {
        const r = row as CalendarEvent
        setEditing(r)
        setEventForm({
          title: r.title,
          event_type: r.event_type,
          start_date: r.start_date,
          end_date: r.end_date,
          description: r.description || '',
          academic_year: r.academic_year ? String(r.academic_year) : '',
        })
        setDlg('event')
      },
      onDelete: (row) => deleteEvent(row as CalendarEvent),
    }),
  ]

  return (
    <>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2, alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }} size="small">
          <InputLabel>Academic year</InputLabel>
          <Select
            label="Academic year"
            value={yearId}
            onChange={(e) => {
              setYearId(e.target.value)
              setEventForm((f) => ({ ...f, academic_year: e.target.value }))
              setHolidayForm((f) => ({ ...f, academic_year: e.target.value }))
            }}
          >
            {years.map((y) => (
              <MenuItem key={y.id} value={String(y.id)}>
                {y.name} {y.is_current ? '(current)' : ''}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 160 }} size="small">
          <InputLabel>Filter type</InputLabel>
          <Select label="Filter type" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <MenuItem value="">All types</MenuItem>
            {EVENT_TYPES.map((t) => (
              <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        {summary && (
          <Chip label={`${summary.working_days} working days`} color="success" variant="outlined" />
        )}
        {summary && (
          <Chip label={`${summary.holiday_days} holiday days`} color="warning" variant="outlined" />
        )}
        <Box sx={{ flexGrow: 1 }} />
        {canManage && (
          <>
            <Button variant="outlined" startIcon={<BeachAccessIcon />} onClick={() => setDlg('holiday')}>
              Mark holiday range
            </Button>
            <Button variant="outlined" startIcon={<UploadFileIcon />} onClick={() => setDlg('bulk')}>
              Bulk CSV
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                setEditing(null)
                setEventForm(emptyEvent(yearId))
                setDlg('event')
              }}
            >
              Add entry
            </Button>
          </>
        )}
      </Box>

      <MonthCalendar
        year={viewYear}
        month={viewMonth}
        events={filteredEvents}
        onPrev={() => shiftMonth(-1)}
        onNext={() => shiftMonth(1)}
      />

      <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>Entries this month</Typography>
      <DataTable rows={filteredEvents} columns={columns} getRowId={(r) => r.id} />

      <FormDialog
        open={dlg === 'event'}
        title={editing ? 'Edit calendar entry' : 'Add calendar entry'}
        onClose={() => { setDlg(null); setEditing(null) }}
        onSubmit={saveEvent}
        loading={loading}
      >
        <TextField fullWidth margin="normal" label="Title" value={eventForm.title} onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Type</InputLabel>
          <Select label="Type" value={eventForm.event_type} onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}>
            {EVENT_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Start date" type="date" value={eventForm.start_date} onChange={(e) => setEventForm({ ...eventForm, start_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="End date" type="date" value={eventForm.end_date} onChange={(e) => setEventForm({ ...eventForm, end_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="Description" multiline minRows={2} value={eventForm.description} onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })} />
      </FormDialog>

      <FormDialog open={dlg === 'holiday'} title="Mark holiday / break (date range)" onClose={() => setDlg(null)} onSubmit={saveHolidayRange} loading={loading}>
        <Alert severity="info" sx={{ mb: 1 }}>Creates one calendar entry from start to end date (e.g. Dashain week, winter break).</Alert>
        <TextField fullWidth margin="normal" label="Title" value={holidayForm.title} onChange={(e) => setHolidayForm({ ...holidayForm, title: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Holiday type</InputLabel>
          <Select label="Holiday type" value={holidayForm.event_type} onChange={(e) => setHolidayForm({ ...holidayForm, event_type: e.target.value })}>
            {EVENT_TYPES.filter((t) => HOLIDAY_TYPES.includes(t.value)).map((t) => (
              <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Start date" type="date" value={holidayForm.start_date} onChange={(e) => setHolidayForm({ ...holidayForm, start_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="End date" type="date" value={holidayForm.end_date} onChange={(e) => setHolidayForm({ ...holidayForm, end_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="Note (optional)" value={holidayForm.description} onChange={(e) => setHolidayForm({ ...holidayForm, description: e.target.value })} />
      </FormDialog>

      <FormDialog open={dlg === 'bulk'} title="Bulk upload holidays & events (CSV)" onClose={() => setDlg(null)} onSubmit={uploadBulk} loading={loading}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Columns: title, event_type, start_date, end_date, description (YYYY-MM-DD). Rows duplicate title+dates are skipped.
        </Alert>
        <Button variant="outlined" size="small" sx={{ mb: 2 }} component="a" href="data:text/csv;charset=utf-8,title%2Cevent_type%2Cstart_date%2Cend_date%2Cdescription%0ADashain%2Cpublic_holiday%2C2025-10-20%2C2025-10-24%2CFestival" download="calendar_template.csv">
          Download sample CSV
        </Button>
        <Button variant="contained" component="label">
          Choose CSV file
          <input type="file" accept=".csv,text/csv" hidden onChange={(e) => setBulkFile(e.target.files?.[0] ?? null)} />
        </Button>
        {bulkFile && <Typography variant="body2" sx={{ mt: 1 }}>{bulkFile.name}</Typography>}
      </FormDialog>
    </>
  )
}

function AcademicYearsPanel({ canManage }: { canManage: boolean }) {
  const [years, setYears] = useState<AcademicYear[]>([])
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ name: '', start_date: '', end_date: '', is_current: false })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/students/academic-years/').then((r) => setYears(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const save = async () => {
    setLoading(true)
    try {
      await api.post('/students/academic-years/', form)
      toast.success('Academic year created')
      setOpen(false)
      load()
    } catch {
      toast.error('Save failed — check dates')
    } finally {
      setLoading(false)
    }
  }

  const setCurrent = async (id: number) => {
    await api.post(`/students/academic-years/${id}/set_current/`)
    toast.success('Current academic year updated')
    load()
  }

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', width: 140 },
    { field: 'start_date', headerName: 'Start', width: 120 },
    { field: 'end_date', headerName: 'End', width: 120 },
    {
      field: 'is_current',
      headerName: 'Current',
      width: 100,
      renderCell: (p) => (p.value ? <Chip label="Current" size="small" color="primary" /> : null),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 140,
      renderCell: (p) =>
        canManage && !p.row.is_current ? (
          <Button size="small" onClick={() => setCurrent(p.row.id)}>Set current</Button>
        ) : null,
    },
  ]

  return (
    <>
      <Alert severity="info" sx={{ mb: 2 }}>
        Define academic years before batches and calendar entries. Only one year should be marked current.
      </Alert>
      {canManage && (
        <Button sx={{ mb: 2 }} variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
          Add academic year
        </Button>
      )}
      <DataTable rows={years} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title="New academic year" onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <TextField fullWidth margin="normal" label="Name (e.g. 2081/082)" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Start date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="End date" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Set as current</InputLabel>
          <Select label="Set as current" value={form.is_current ? 'yes' : 'no'} onChange={(e) => setForm({ ...form, is_current: e.target.value === 'yes' })}>
            <MenuItem value="no">No</MenuItem>
            <MenuItem value="yes">Yes</MenuItem>
          </Select>
        </FormControl>
      </FormDialog>
    </>
  )
}

export default function CalendarPage() {
  const { canCreate, canViewNav } = usePermissions()
  const canManage = canCreate('calendar')

  if (!canViewNav('calendar')) {
    return <Typography>You do not have access to the calendar module.</Typography>
  }

  return (
    <>
      <PageHeader
        title="Academic calendar"
        subtitle="Academic years, holidays, term breaks, exams, and institute events"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Calendar' }]}
      />
      <PageTabs
        tabs={[
          { id: 'calendar', label: 'Calendar', panel: <CalendarMainPanel canManage={canManage} /> },
          { id: 'years', label: 'Academic years', panel: <AcademicYearsPanel canManage={canManage} /> },
        ]}
      />
    </>
  )
}
