import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  Chip,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Switch,
  TextField,
  Typography,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import EmailIcon from '@mui/icons-material/Email'
import SmsIcon from '@mui/icons-material/Sms'
import WebIcon from '@mui/icons-material/Web'
import PhoneAndroidIcon from '@mui/icons-material/PhoneAndroid'
import AddIcon from '@mui/icons-material/Add'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import FormSection from '../components/FormSection'
import DetailDrawer from '../components/DetailDrawer'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

const CHANNELS = [
  { value: 'web', label: 'Web notification' },
  { value: 'mobile', label: 'Mobile app notification' },
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
]

const ROLE_TARGETS = [
  { value: 'student', label: 'Students' },
  { value: 'teacher', label: 'Teachers' },
  { value: 'admin_staff', label: 'Admin staff' },
]

const emptyForm = () => ({
  title: '',
  body: '',
  status: 'draft',
  is_important: false,
  channels: ['web'] as string[],
  target_roles: [] as string[],
  target_all_students: false,
  target_all_teachers: false,
  target_all_admin_staff: false,
  target_department_ids: [] as number[],
  target_batch_ids: [] as number[],
  target_shift_ids: [] as number[],
})

export default function AnnouncementsPage() {
  const { canCreate, canEdit } = usePermissions()
  const [rows, setRows] = useState([])
  const [departments, setDepartments] = useState<{ id: number; name: string }[]>([])
  const [batches, setBatches] = useState<{ id: number; name: string }[]>([])
  const [shifts, setShifts] = useState<{ id: number; name: string; timing_label?: string; is_active?: boolean }[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null)
  const [form, setForm] = useState(emptyForm())
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null)
  const [delivery, setDelivery] = useState<{ channels: { channel: string; sent: number; read: number }[]; total_recipients?: number } | null>(null)
  const [deliveryLoading, setDeliveryLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/announcements/').then((r) => setRows(r.data.results || r.data))
    api.get('/students/departments/').then((r) => setDepartments(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
    api.get('/students/shifts/').then((r) => setShifts(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm())
    setOpen(true)
  }

  const openEdit = (row: Record<string, unknown>) => {
    setEditing(row)
    setForm({
      title: row.title as string,
      body: row.body as string,
      status: row.status as string,
      is_important: row.is_important as boolean,
      channels: (row.channels as string[]) || ['web'],
      target_roles: (row.target_roles as string[]) || [],
      target_all_students: !!row.target_all_students,
      target_all_teachers: !!row.target_all_teachers,
      target_all_admin_staff: !!row.target_all_admin_staff,
      target_department_ids: (row.target_department_ids as number[]) || [],
      target_batch_ids: (row.target_batch_ids as number[]) || [],
      target_shift_ids: (row.target_shift_ids as number[]) || [],
    })
    setOpen(true)
  }

  const openDetail = (row: Record<string, unknown>) => {
    setDetail(row)
    setDelivery(null)
    if (row.status === 'published') {
      setDeliveryLoading(true)
      api.get(`/announcements/${row.id}/delivery-report/`)
        .then((r) => setDelivery(r.data))
        .catch(() => setDelivery(null))
        .finally(() => setDeliveryLoading(false))
    }
  }

  const channelIcon = (ch: string) => {
    if (ch === 'email') return <EmailIcon fontSize="small" />
    if (ch === 'sms') return <SmsIcon fontSize="small" />
    if (ch === 'mobile') return <PhoneAndroidIcon fontSize="small" />
    return <WebIcon fontSize="small" />
  }

  const publish = async (id: number) => {
    try {
      const r = await api.post(`/announcements/${id}/publish/`)
      toast.success(`Published to ${r.data.recipients_notified ?? 0} recipients`)
      load()
    } catch {
      toast.error('Publish failed')
    }
  }

  const save = async () => {
    setLoading(true)
    try {
      if (editing) {
        await api.patch(`/announcements/${editing.id}/`, form)
        toast.success('Announcement updated')
      } else {
        await api.post('/announcements/', form)
        toast.success('Announcement created')
      }
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
      { field: 'title', headerName: 'Title', flex: 1, minWidth: 200 },
      {
        field: 'channels',
        headerName: 'Channels',
        width: 180,
        renderCell: (p) => (
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', py: 0.5 }}>
            {(p.value as string[] || []).map((c) => (
              <Chip key={c} label={c} size="small" variant="outlined" />
            ))}
          </Box>
        ),
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 120,
        renderCell: (p) => (
          <Chip label={p.value} size="small" color={p.value === 'published' ? 'success' : 'default'} variant="outlined" />
        ),
      },
      {
        field: 'is_important',
        headerName: 'Priority',
        width: 100,
        renderCell: (p) => (p.value ? <Chip label="Important" color="error" size="small" /> : null),
      },
      ...buildActionColumns({
        onView: openDetail,
        onEdit: openEdit,
        canView: true,
        canEdit: canEdit('announcements'),
      }),
      {
        field: 'publish',
        headerName: 'Publish',
        width: 100,
        renderCell: (p) =>
          p.row.status === 'draft' && canEdit('announcements') ? (
            <Button size="small" variant="outlined" onClick={() => publish(p.row.id)}>Publish</Button>
          ) : null,
      },
    ],
    [canEdit],
  )

  return (
    <>
      <PageHeader
        title="Announcements"
        subtitle="SMS, email, web, and mobile notifications with batch, faculty, or shift targeting"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Announcements' }]}
        action={canCreate('announcements') ? <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>Add announcement</Button> : undefined}
      />
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title={editing ? 'Edit announcement' : 'Add announcement'} onClose={() => setOpen(false)} onSubmit={save} loading={loading} maxWidth="md">
        <TextField fullWidth margin="normal" label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <TextField fullWidth margin="normal" label="Body" multiline rows={4} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />

        <FormSection title="Delivery channels">
          <FormGroup row>
            {CHANNELS.map((ch) => (
              <FormControlLabel
                key={ch.value}
                control={
                  <Checkbox
                    checked={form.channels.includes(ch.value)}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...form.channels, ch.value]
                        : form.channels.filter((c) => c !== ch.value)
                      setForm({ ...form, channels: next })
                    }}
                  />
                }
                label={ch.label}
              />
            ))}
          </FormGroup>
        </FormSection>

        <FormSection title="Audience">
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Send to everyone in a role, or narrow students by faculty (department), batch, or shift.
          </Typography>
          <FormControlLabel
            control={<Switch checked={form.target_all_students} onChange={(e) => setForm({ ...form, target_all_students: e.target.checked })} />}
            label="All students"
          />
          <FormControlLabel
            control={<Switch checked={form.target_all_teachers} onChange={(e) => setForm({ ...form, target_all_teachers: e.target.checked })} />}
            label="All teachers"
          />
          <FormControlLabel
            control={<Switch checked={form.target_all_admin_staff} onChange={(e) => setForm({ ...form, target_all_admin_staff: e.target.checked })} />}
            label="All admin staff"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Also include roles</InputLabel>
            <Select
              multiple
              label="Also include roles"
              value={form.target_roles}
              onChange={(e) => setForm({ ...form, target_roles: e.target.value as string[] })}
              renderValue={(sel) => (sel as string[]).join(', ')}
            >
              {ROLE_TARGETS.map((r) => <MenuItem key={r.value} value={r.value}>{r.label}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Faculty / departments (students)</InputLabel>
            <Select
              multiple
              label="Faculty / departments (students)"
              value={form.target_department_ids}
              onChange={(e) => setForm({ ...form, target_department_ids: e.target.value as number[] })}
              renderValue={(sel) => departments.filter((d) => (sel as number[]).includes(d.id)).map((d) => d.name).join(', ')}
            >
              {departments.map((d) => <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Batches (students)</InputLabel>
            <Select
              multiple
              label="Batches (students)"
              value={form.target_batch_ids}
              onChange={(e) => setForm({ ...form, target_batch_ids: e.target.value as number[] })}
              renderValue={(sel) => batches.filter((b) => (sel as number[]).includes(b.id)).map((b) => b.name).join(', ')}
            >
              {batches.map((b) => <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Shifts (students)</InputLabel>
            <Select
              multiple
              label="Shifts (students)"
              value={form.target_shift_ids}
              onChange={(e) => setForm({ ...form, target_shift_ids: e.target.value as number[] })}
              renderValue={(sel) =>
                shifts
                  .filter((s) => (sel as number[]).includes(s.id))
                  .map((s) => (s.timing_label ? `${s.name} (${s.timing_label})` : s.name))
                  .join(', ')
              }
            >
              {shifts
              .filter((s) => s.is_active !== false)
              .map((s) => (
                <MenuItem key={s.id} value={s.id}>
                  {s.name}{s.timing_label ? ` · ${s.timing_label}` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </FormSection>

        <FormControl fullWidth margin="normal">
          <InputLabel>Status</InputLabel>
          <Select label="Status" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <MenuItem value="draft">Draft</MenuItem>
            <MenuItem value="scheduled">Scheduled</MenuItem>
            <MenuItem value="published">Published</MenuItem>
            <MenuItem value="archived">Archived</MenuItem>
          </Select>
        </FormControl>
        <FormControlLabel
          control={<Switch checked={form.is_important} onChange={(e) => setForm({ ...form, is_important: e.target.checked })} />}
          label="Mark as important"
        />
      </FormDialog>

      <DetailDrawer
        open={!!detail}
        onClose={() => setDetail(null)}
        title={detail?.title as string}
        subtitle={detail?.status as string}
        width={520}
        actions={
          detail?.status === 'draft' && canEdit('announcements') ? (
            <Button size="small" variant="contained" onClick={() => publish(detail.id as number)}>Publish</Button>
          ) : undefined
        }
      >
        {detail && (
          <Box>
            <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>{detail.body as string}</Typography>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
              {((detail.channels as string[]) || []).map((c) => (
                <Chip key={c} label={c} size="small" variant="outlined" />
              ))}
            </Box>
            {detail.status === 'published' && (
              <Accordion defaultExpanded disableGutters variant="outlined">
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>Delivery report</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {deliveryLoading && (
                    <Box>
                      <Skeleton height={32} />
                      <Skeleton height={32} />
                    </Box>
                  )}
                  {!deliveryLoading && !delivery?.channels?.length && (
                    <Typography variant="body2" color="text.secondary">
                      Delivery data not yet available.
                    </Typography>
                  )}
                  {!deliveryLoading && delivery?.channels?.map((row) => (
                    <Grid container key={row.channel} spacing={1} alignItems="center" sx={{ mb: 1 }}>
                      <Grid item xs={4} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        {channelIcon(row.channel)}
                        <Typography variant="body2" textTransform="capitalize">{row.channel}</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Sent</Typography>
                        <Typography fontWeight={700}>{row.sent}</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Read</Typography>
                        <Typography fontWeight={700}>{row.read}</Typography>
                      </Grid>
                    </Grid>
                  ))}
                  {!deliveryLoading && delivery?.total_recipients != null && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Target audience: {delivery.total_recipients} users
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
            )}
          </Box>
        )}
      </DetailDrawer>
    </>
  )
}
