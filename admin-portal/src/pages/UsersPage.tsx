import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Button,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  Box,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import { buildActionColumns } from '../components/GridActions'
import api from '../api/client'
import { ROLE_LABELS } from '../config/permissions'

type UserRow = {
  id: string
  email: string
  full_name: string
  role: string
  role_label?: string
  phone?: string
  is_active: boolean
  first_name?: string
  last_name?: string
  allow_web_portal?: boolean | null
  allow_mobile_app?: boolean | null
  effective_channel_access?: { web_portal: boolean; mobile_app: boolean }
}

type RoleOption = { value: string; label: string }

const emptyForm = {
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  phone: '',
  role: 'admin_staff',
  is_active: true,
  allow_web_portal: 'inherit',
  allow_mobile_app: 'inherit',
}

export default function UsersPage() {
  const [rows, setRows] = useState<UserRow[]>([])
  const [roles, setRoles] = useState<RoleOption[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<UserRow | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(false)
  const [accessMatrix, setAccessMatrix] = useState<Record<string, Record<string, string[]>> | null>(null)
  const [channelAccess, setChannelAccess] = useState<Record<string, { web_portal: boolean; mobile_app: boolean }> | null>(null)

  const load = useCallback(() => {
    api.get('/auth/users/').then((r) => setRows(r.data.results || r.data))
  }, [])

  useEffect(() => {
    load()
    api.get('/auth/users/role_options/').then((r) => {
      setRoles(r.data.roles || [])
      setAccessMatrix(r.data.access_matrix || null)
      setChannelAccess(r.data.channel_access || null)
    })
  }, [load])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setOpen(true)
  }

  const openEdit = (row: UserRow) => {
    setEditing(row)
    setForm({
      email: row.email,
      password: '',
      first_name: row.first_name || row.full_name?.split(' ')[0] || '',
      last_name: row.last_name || row.full_name?.split(' ').slice(1).join(' ') || '',
      phone: row.phone || '',
      role: row.role,
      is_active: row.is_active ?? true,
      allow_web_portal: row.allow_web_portal == null ? 'inherit' : row.allow_web_portal ? 'allow' : 'deny',
      allow_mobile_app: row.allow_mobile_app == null ? 'inherit' : row.allow_mobile_app ? 'allow' : 'deny',
    })
    setOpen(true)
  }

  const save = async () => {
    setLoading(true)
    try {
      if (editing) {
        const payload: Record<string, unknown> = {
          first_name: form.first_name,
          last_name: form.last_name,
          phone: form.phone,
          role: form.role,
          is_active: form.is_active,
          allow_web_portal: form.allow_web_portal === 'inherit' ? null : form.allow_web_portal === 'allow',
          allow_mobile_app: form.allow_mobile_app === 'inherit' ? null : form.allow_mobile_app === 'allow',
        }
        if (form.password) payload.password = form.password
        await api.patch(`/auth/users/${editing.id}/`, payload)
        toast.success('User updated')
      } else {
        await api.post('/auth/users/', {
          email: form.email,
          password: form.password,
          first_name: form.first_name,
          last_name: form.last_name,
          phone: form.phone,
          role: form.role,
          is_active: form.is_active,
          allow_web_portal: form.allow_web_portal === 'inherit' ? null : form.allow_web_portal === 'allow',
          allow_mobile_app: form.allow_mobile_app === 'inherit' ? null : form.allow_mobile_app === 'allow',
        })
        toast.success('User created')
      }
      setOpen(false)
      load()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string; email?: string[] } } })?.response?.data
      toast.error(msg?.detail || msg?.email?.[0] || 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  const deactivate = async (row: UserRow) => {
    if (!confirm(`Deactivate ${row.full_name}?`)) return
    await api.delete(`/auth/users/${row.id}/`)
    toast.success('User deactivated')
    load()
  }

  const columns: GridColDef[] = useMemo(
    () => [
      { field: 'full_name', headerName: 'Name', width: 180 },
      { field: 'email', headerName: 'Email', width: 220 },
      {
        field: 'role',
        headerName: 'Role',
        width: 160,
        renderCell: (p) => (
          <Chip
            label={p.row.role_label || ROLE_LABELS[p.value as string] || p.value}
            size="small"
            variant="outlined"
            color={p.value === 'teacher' ? 'primary' : p.value === 'admin_staff' ? 'secondary' : 'default'}
          />
        ),
      },
      { field: 'phone', headerName: 'Phone', width: 130 },
      {
        field: 'is_active',
        headerName: 'Status',
        width: 100,
        renderCell: (p) => (
          <Chip label={p.value ? 'Active' : 'Inactive'} size="small" color={p.value ? 'success' : 'default'} />
        ),
      },
      {
        field: 'web_access',
        headerName: 'Web Portal',
        width: 120,
        renderCell: (p) => (
          <Chip
            label={p.row.is_active && p.row.effective_channel_access?.web_portal ? 'Allowed' : 'Denied'}
            size="small"
            color={p.row.is_active && p.row.effective_channel_access?.web_portal ? 'success' : 'default'}
          />
        ),
      },
      {
        field: 'mobile_access',
        headerName: 'Mobile App',
        width: 120,
        renderCell: (p) => (
          <Chip
            label={p.row.is_active && p.row.effective_channel_access?.mobile_app ? 'Allowed' : 'Denied'}
            size="small"
            color={p.row.is_active && p.row.effective_channel_access?.mobile_app ? 'success' : 'default'}
          />
        ),
      },
      ...buildActionColumns<UserRow>({
        onEdit: openEdit,
        onDelete: deactivate,
        canEdit: true,
        canDelete: true,
      }),
    ],
    [],
  )

  return (
    <>
      <PageHeader
        title="User management"
        subtitle="Create reception staff, teachers, and students — access follows their role"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Users' }]}
        action={
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Add user
          </Button>
        }
      />

      {accessMatrix && (
        <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Role access summary
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(ROLE_LABELS)
              .filter(([k]) => k !== 'student' && k !== 'parent')
              .map(([key, label]) => (
                <Chip key={key} label={label} size="small" variant="outlined" />
              ))}
          </Box>
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Reception (admin_staff): students, enrollment, fees, attendance. Teachers: attendance & results.
            Only Super Admin can manage users and settings.
          </Typography>
          {channelAccess && (
            <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
              Role defaults — Teacher/Admin/Student can be set for Web Portal and Mobile App. Per-user overrides available below.
            </Typography>
          )}
        </Alert>
      )}

      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />

      <FormDialog
        open={open}
        title={editing ? 'Edit user' : 'Create user'}
        onClose={() => setOpen(false)}
        onSubmit={save}
        loading={loading}
        submitLabel={editing ? 'Update' : 'Create'}
      >
        {!editing && (
          <TextField
            fullWidth margin="normal" label="Email" type="email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        )}
        <TextField
          fullWidth margin="normal"
          label={editing ? 'New password (optional)' : 'Password'}
          type="password"
          required={!editing}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <TextField
          fullWidth margin="normal" label="First name" required
          value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })}
        />
        <TextField
          fullWidth margin="normal" label="Last name" required
          value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })}
        />
        <TextField
          fullWidth margin="normal" label="Phone"
          value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>Role</InputLabel>
          <Select
            label="Role"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            {roles.map((r) => (
              <MenuItem key={r.value} value={r.value}>{r.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Status</InputLabel>
          <Select
            label="Status"
            value={form.is_active ? 'active' : 'inactive'}
            onChange={(e) => setForm({ ...form, is_active: e.target.value === 'active' })}
          >
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Web portal access</InputLabel>
          <Select
            label="Web portal access"
            value={form.allow_web_portal}
            onChange={(e) => setForm({ ...form, allow_web_portal: e.target.value })}
          >
            <MenuItem value="inherit">Inherit role default</MenuItem>
            <MenuItem value="allow">Allow</MenuItem>
            <MenuItem value="deny">Deny</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Mobile app access</InputLabel>
          <Select
            label="Mobile app access"
            value={form.allow_mobile_app}
            onChange={(e) => setForm({ ...form, allow_mobile_app: e.target.value })}
          >
            <MenuItem value="inherit">Inherit role default</MenuItem>
            <MenuItem value="allow">Allow</MenuItem>
            <MenuItem value="deny">Deny</MenuItem>
          </Select>
        </FormControl>
      </FormDialog>
    </>
  )
}
