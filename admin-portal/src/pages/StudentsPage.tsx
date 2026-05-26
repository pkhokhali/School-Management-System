import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Avatar,
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import FormSection from '../components/FormSection'
import DetailDrawer from '../components/DetailDrawer'
import StudentFeesTab from '../components/StudentFeesTab'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import api from '../api/client'

export default function StudentsPage() {
  const { canCreate, canEdit } = usePermissions()
  const canManageFees = canCreate('fees') || canEdit('fees')
  const [searchParams, setSearchParams] = useSearchParams()
  const [rows, setRows] = useState<Record<string, unknown>[]>([])
  const [batches, setBatches] = useState<{ id: number; name: string }[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null)
  const [form, setForm] = useState({
    email: '', password: '', first_name: '', last_name: '', phone: '', batch_id: '',
    date_of_birth: '', guardian_name: '', guardian_phone: '', guardian_email: '', guardian_relation: '',
  })
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null)
  const [drawerTab, setDrawerTab] = useState(0)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)

  const load = useCallback(() => {
    api.get('/students/').then((r) => setRows(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const openStudentById = useCallback(async (id: string) => {
    const fromRows = rows.find((r) => String(r.id) === id)
    if (fromRows) {
      setDetail(fromRows)
      setDrawerTab(0)
      return
    }
    try {
      const { data } = await api.get(`/students/${id}/`)
      setDetail(data)
      setDrawerTab(0)
    } catch {
      toast.error('Student not found')
    }
  }, [rows])

  useEffect(() => {
    const openId = searchParams.get('open')
    if (openId) openStudentById(openId)
  }, [searchParams, openStudentById])

  const closeDetail = () => {
    setDetail(null)
    if (searchParams.get('open')) {
      searchParams.delete('open')
      setSearchParams(searchParams)
    }
  }

  const openCreate = () => {
    setEditing(null)
    setForm({ email: '', password: '', first_name: '', last_name: '', phone: '', batch_id: '', date_of_birth: '', guardian_name: '', guardian_phone: '', guardian_email: '', guardian_relation: '' })
    setOpen(true)
  }

  const openEdit = (row: Record<string, unknown>) => {
    setEditing(row)
    const name = (row.full_name as string)?.split(' ') || []
    setForm({
      email: row.email as string,
      password: '',
      first_name: name[0] || '',
      last_name: name.slice(1).join(' ') || '',
      phone: (row.phone as string) || '',
      batch_id: String(row.batch || ''),
      date_of_birth: (row.date_of_birth as string) || '',
      guardian_name: (row.guardian_name as string) || '',
      guardian_phone: (row.guardian_phone as string) || '',
      guardian_email: (row.guardian_email as string) || '',
      guardian_relation: (row.guardian_relation as string) || '',
    })
    setOpen(true)
  }

  const save = async () => {
    setLoading(true)
    try {
      if (editing) {
        await api.patch(`/students/${editing.id}/`, {
          first_name: form.first_name,
          last_name: form.last_name,
          phone: form.phone,
          batch: form.batch_id ? Number(form.batch_id) : null,
          date_of_birth: form.date_of_birth || null,
          guardian_name: form.guardian_name,
          guardian_phone: form.guardian_phone,
          guardian_email: form.guardian_email,
          guardian_relation: form.guardian_relation,
        })
        toast.success('Student updated')
      } else {
        await api.post('/students/register/', {
          ...form,
          batch_id: form.batch_id ? Number(form.batch_id) : undefined,
        })
        toast.success('Student created')
      }
      const studentId = editing?.id
      if (avatarFile && studentId) {
        const fd = new FormData()
        fd.append('avatar', avatarFile)
        await api.post(`/students/${studentId}/upload-avatar/`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      }
      setOpen(false)
      setAvatarFile(null)
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'enrollment_number', headerName: 'Enrollment #', width: 140 },
      { field: 'full_name', headerName: 'Name', width: 200 },
      { field: 'email', headerName: 'Email', width: 220 },
      { field: 'batch_name', headerName: 'Batch', width: 150 },
      ...buildActionColumns({
        onView: (row) => {
          setDetail(row)
          setDrawerTab(0)
          setSearchParams({ open: String(row.id) })
        },
        onEdit: openEdit,
        canView: true,
        canEdit: canEdit('students'),
        canDelete: false,
      }),
    ],
    [canEdit, setSearchParams],
  )

  return (
    <>
      <PageHeader
        title="Students"
        subtitle="Manage student profiles, batches, and enrollment numbers"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Students' }]}
        action={
          canCreate('students') ? (
            <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
              Add student
            </Button>
          ) : undefined
        }
      />
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title={editing ? 'Edit student' : 'Add student'} onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        {!editing && (
          <>
            <TextField fullWidth margin="normal" label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <TextField fullWidth margin="normal" label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </>
        )}
        <TextField fullWidth margin="normal" label="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <TextField fullWidth margin="normal" label="Date of birth" type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} InputLabelProps={{ shrink: true }} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Batch</InputLabel>
          <Select label="Batch" value={form.batch_id} onChange={(e) => setForm({ ...form, batch_id: e.target.value })}>
            <MenuItem value="">None</MenuItem>
            {batches.map((b) => <MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormSection title="Profile picture">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Avatar src={(editing?.avatar_url as string) || undefined} sx={{ width: 56, height: 56 }}>
              {(editing?.full_name as string)?.[0]}
            </Avatar>
            <Button variant="outlined" component="label" size="small">
              {avatarFile ? avatarFile.name : 'Upload photo'}
              <input type="file" hidden accept="image/*" onChange={(e) => setAvatarFile(e.target.files?.[0] || null)} />
            </Button>
          </Box>
        </FormSection>
        <FormSection title="Guardian / parent">
          <TextField fullWidth margin="normal" label="Guardian name" value={form.guardian_name} onChange={(e) => setForm({ ...form, guardian_name: e.target.value })} />
          <TextField fullWidth margin="normal" label="Relation" value={form.guardian_relation} onChange={(e) => setForm({ ...form, guardian_relation: e.target.value })} />
          <TextField fullWidth margin="normal" label="Guardian phone" value={form.guardian_phone} onChange={(e) => setForm({ ...form, guardian_phone: e.target.value })} />
          <TextField fullWidth margin="normal" label="Guardian email" value={form.guardian_email} onChange={(e) => setForm({ ...form, guardian_email: e.target.value })} />
        </FormSection>
      </FormDialog>

      <DetailDrawer
        open={!!detail}
        onClose={closeDetail}
        title={detail?.full_name as string}
        subtitle={detail?.enrollment_number as string}
        width={520}
        actions={
          canEdit('students') ? (
            <>
              <Button size="small" variant="outlined" component="label">
                Photo
                <input type="file" hidden accept="image/*" onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f && detail) {
                    const fd = new FormData()
                    fd.append('avatar', f)
                    api.post(`/students/${detail.id}/upload-avatar/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
                      .then(() => { toast.success('Photo updated'); load(); closeDetail() })
                      .catch(() => toast.error('Upload failed'))
                  }
                }} />
              </Button>
              <Button size="small" variant="contained" onClick={() => { openEdit(detail!); closeDetail() }}>Edit</Button>
            </>
          ) : undefined
        }
      >
        {detail && (
          <Box>
            <Tabs value={drawerTab} onChange={(_, v) => setDrawerTab(v)} sx={{ mb: 2 }}>
              <Tab label="Profile" />
              <Tab label="Fees" />
            </Tabs>
            {drawerTab === 0 && (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar src={(detail.avatar_url as string) || undefined} sx={{ width: 72, height: 72 }} />
                  <Box>
                    <Typography variant="subtitle1" fontWeight={700}>{detail.full_name as string}</Typography>
                    <Typography variant="body2" color="text.secondary">{detail.enrollment_number as string}</Typography>
                  </Box>
                </Box>
                <Grid container spacing={2}>
                  {([
                    ['Email', detail.email],
                    ['Phone', detail.phone],
                    ['Batch', detail.batch_name],
                    ['Date of birth', detail.date_of_birth],
                    ['Guardian', detail.guardian_name],
                    ['Guardian phone', detail.guardian_phone],
                  ] as [string, unknown][]).map(([label, val]) => (
                    <Grid item xs={6} key={label}>
                      <Typography variant="caption" color="text.secondary">{label}</Typography>
                      <Typography variant="body2" fontWeight={600}>{val != null && val !== '' ? String(val) : '—'}</Typography>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
            {drawerTab === 1 && (
              <StudentFeesTab
                studentId={detail.id as number}
                enrollmentNumber={detail.enrollment_number as string}
                canManage={canManageFees}
              />
            )}
          </Box>
        )}
      </DetailDrawer>
    </>
  )
}
