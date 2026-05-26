import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import ReceiptIcon from '@mui/icons-material/Receipt'
import { GridColDef } from '@mui/x-data-grid'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import FormDialog from '../components/FormDialog'
import PageTabs from '../components/PageTabs'
import { buildActionColumns } from '../components/GridActions'
import { usePermissions } from '../hooks/usePermissions'
import { useAuthStore } from '../store/authStore'
import { useFeatureStore } from '../store/featureStore'
import api from '../api/client'

type Row = Record<string, unknown>

function SummaryPanel() {
  const [stats, setStats] = useState<Record<string, unknown>>({})

  useEffect(() => {
    api.get('/fees/summary/').then((r) => setStats(r.data)).catch(() => {})
  }, [])

  const cards = [
    { label: 'Collected today (NPR)', value: stats.collected_today },
    { label: 'Fonepay today', value: stats.fonepay_today },
    { label: 'Collected this month', value: stats.collected_month },
    { label: 'Outstanding total', value: stats.outstanding_total },
    { label: 'Overdue accounts', value: stats.overdue_count },
    { label: 'Refunds pending', value: stats.pending_refunds, link: '/fees' },
    { label: 'Installments due (7d)', value: stats.installments_due_this_week, link: '/fees' },
    { label: 'Installment amount due', value: stats.installments_due_amount },
  ]

  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      {cards.map((c) => (
        <Grid item xs={12} sm={6} md={4} key={c.label}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="caption" color="text.secondary">{c.label}</Typography>
              <Typography variant="h5" fontWeight={700}>{String(c.value ?? '—')}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}

function FeeHeadsPanel({ canManage }: { canManage: boolean }) {
  const [rows, setRows] = useState<Row[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Row | null>(null)
  const [form, setForm] = useState({ name: '', code: '', description: '' })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/fees/heads/').then((r) => setRows(r.data.results || r.data)), [])

  useEffect(() => { load() }, [load])

  const save = async () => {
    setLoading(true)
    try {
      if (editing) await api.patch(`/fees/heads/${editing.id}/`, form)
      else await api.post('/fees/heads/', form)
      toast.success('Fee head saved')
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
      { field: 'code', headerName: 'Code', width: 100 },
      { field: 'name', headerName: 'Fee head', flex: 1 },
      { field: 'description', headerName: 'Description', flex: 1 },
      ...buildActionColumns({
        canEdit: canManage,
        onEdit: (row) => {
          setEditing(row)
          setForm({ name: row.name as string, code: row.code as string, description: (row.description as string) || '' })
          setOpen(true)
        },
      }),
    ],
    [canManage],
  )

  return (
    <>
      {canManage && (
        <Button sx={{ mb: 2 }} variant="outlined" startIcon={<AddIcon />} onClick={() => { setEditing(null); setForm({ name: '', code: '', description: '' }); setOpen(true) }}>
          Add fee head
        </Button>
      )}
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title={editing ? 'Edit fee head' : 'Add fee head'} onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <TextField fullWidth margin="normal" label="Name (e.g. Tuition)" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <TextField fullWidth margin="normal" label="Code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
        <TextField fullWidth margin="normal" label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
      </FormDialog>
    </>
  )
}

function FeeStructuresPanel({ canManage }: { canManage: boolean }) {
  const [rows, setRows] = useState<Row[]>([])
  const [courses, setCourses] = useState<{ id: number; name: string; code: string }[]>([])
  const [heads, setHeads] = useState<{ id: number; name: string }[]>([])
  const [batches, setBatches] = useState<{ id: number; name: string }[]>([])
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ course: '', batch: '', fee_head: '', amount: '', semester: '' })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/fees/structures/').then((r) => setRows(r.data.results || r.data))
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
    api.get('/fees/heads/').then((r) => setHeads(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const save = async () => {
    setLoading(true)
    try {
      await api.post('/fees/structures/', {
        course: Number(form.course),
        batch: form.batch ? Number(form.batch) : null,
        fee_head: Number(form.fee_head),
        amount: form.amount,
        semester: form.semester ? Number(form.semester) : null,
      })
      toast.success('Fee structure created')
      setOpen(false)
      load()
    } catch {
      toast.error('Create failed')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = [
    { field: 'course_name', headerName: 'Program', flex: 1, minWidth: 140 },
    { field: 'fee_head_name', headerName: 'Fee head', width: 130 },
    { field: 'amount', headerName: 'Amount (NPR)', width: 120 },
    { field: 'semester', headerName: 'Sem', width: 60 },
    { field: 'batch_name', headerName: 'Batch', width: 110 },
  ]

  return (
    <>
      {canManage && (
        <>
          <Button sx={{ mb: 2, mr: 1 }} variant="outlined" startIcon={<AddIcon />} onClick={() => { setForm({ course: '', batch: '', fee_head: '', amount: '', semester: '' }); setOpen(true) }}>
            Add fee structure
          </Button>
        </>
      )}
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title="Link fee to program" onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Program</InputLabel>
          <Select label="Program" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })}>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Fee head</InputLabel>
          <Select label="Fee head" value={form.fee_head} onChange={(e) => setForm({ ...form, fee_head: e.target.value })}>
            {heads.map((h) => <MenuItem key={h.id} value={String(h.id)}>{h.name}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Amount (NPR)" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <TextField fullWidth margin="normal" label="Semester (optional)" type="number" value={form.semester || ''} onChange={(e) => setForm({ ...form, semester: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Batch (optional)</InputLabel>
          <Select label="Batch (optional)" value={form.batch} onChange={(e) => setForm({ ...form, batch: e.target.value })}>
            <MenuItem value="">All batches</MenuItem>
            {batches.map((b) => <MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>)}
          </Select>
        </FormControl>
      </FormDialog>
    </>
  )
}

function FeeAssignmentsPanel({ canManage, enrollmentFilter }: { canManage: boolean; enrollmentFilter: string }) {
  const [rows, setRows] = useState<Row[]>([])
  const [students, setStudents] = useState<Row[]>([])
  const [structures, setStructures] = useState<Row[]>([])
  const [search, setSearch] = useState(enrollmentFilter)
  const [open, setOpen] = useState(false)
  const [payOpen, setPayOpen] = useState<Row | null>(null)
  const [form, setForm] = useState({ student: '', fee_structure: '', total_amount: '', discount_amount: '0', due_date: '' })
  const [payForm, setPayForm] = useState({ amount: '', mode: 'cash', transaction_ref: '', cheque_number: '', gateway_ref: '' })
  const [loading, setLoading] = useState(false)
  const paymentsOnlineEnabled = useFeatureStore((s) => s.isEnabled('payments_online'))

  const load = useCallback(() => {
    const params: Record<string, string> = {}
    if (search) params.enrollment_number = search
    api.get('/fees/assignments/', { params }).then((r) => setRows(r.data.results || r.data))
    api.get('/students/').then((r) => setStudents(r.data.results || r.data))
    api.get('/fees/structures/').then((r) => setStructures(r.data.results || r.data))
  }, [search])

  useEffect(() => {
    setSearch(enrollmentFilter)
  }, [enrollmentFilter])

  useEffect(() => { load() }, [load])

  const bulkBill = async () => {
    try {
      const { data } = await api.post('/fees/assignments/bulk-from-enrollment/', { due_date: new Date().toISOString().slice(0, 10) })
      toast.success(`Billed ${data.created} assignment(s), skipped ${data.skipped}`)
      load()
    } catch {
      toast.error('Bulk billing failed')
    }
  }

  const save = async () => {
    setLoading(true)
    try {
      await api.post('/fees/assignments/', {
        student: Number(form.student),
        fee_structure: Number(form.fee_structure),
        total_amount: form.total_amount,
        discount_amount: form.discount_amount || 0,
        due_date: form.due_date,
      })
      toast.success('Fee assigned')
      setOpen(false)
      load()
    } catch {
      toast.error('Assign failed')
    } finally {
      setLoading(false)
    }
  }

  const recordPayment = async () => {
    if (!payOpen) return
    setLoading(true)
    try {
      const { data } = await api.post('/fees/payments/', {
        student_fee: payOpen.id,
        amount: payForm.amount,
        mode: payForm.mode,
        transaction_ref: payForm.transaction_ref,
        gateway_ref: payForm.gateway_ref || payForm.transaction_ref,
        cheque_number: payForm.cheque_number,
      })
      toast.success(`Payment recorded — receipt ${data.receipt_id}`)
      setPayOpen(null)
      load()
    } catch {
      toast.error('Payment failed')
    } finally {
      setLoading(false)
    }
  }

  const downloadReceipt = (paymentId: number) => {
    window.open(`/api/v1/fees/payments/${paymentId}/receipt-pdf/`, '_blank')
  }

  const initiateFonepay = async () => {
    if (!payOpen) return
    try {
      const { data } = await api.post('/fees/online/initiate/', {
        gateway: 'fonepay',
        student_fee_id: payOpen.id,
      })
      if (data.payment_url) window.open(data.payment_url, '_blank')
      if (data.ref) setPayForm((f) => ({ ...f, gateway_ref: data.ref, transaction_ref: data.ref }))
      toast.success('Fonepay initiated. Complete payment then confirm txn ID.')
    } catch {
      toast.error('Unable to start Fonepay payment')
    }
  }

  const confirmFonepay = async () => {
    if (!payOpen) return
    if (!payForm.gateway_ref) {
      toast.error('Enter Fonepay transaction ID first')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/fees/fonepay/confirm/', {
        student_fee_id: payOpen.id,
        amount: payForm.amount,
        fonepay_txn_id: payForm.gateway_ref,
      })
      toast.success(`Fonepay confirmed — receipt ${data.receipt_id}`)
      setPayOpen(null)
      load()
    } catch {
      toast.error('Fonepay confirmation failed')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = [
    { field: 'enrollment_number', headerName: 'ID', width: 110 },
    { field: 'student_name', headerName: 'Student', width: 160 },
    { field: 'fee_head_name', headerName: 'Fee head', width: 120 },
    { field: 'course_name', headerName: 'Program', width: 130 },
    { field: 'total_amount', headerName: 'Total', width: 90 },
    { field: 'semester', headerName: 'Sem', width: 55 },
    { field: 'scholarship_name', headerName: 'Scholarship', width: 110 },
    { field: 'discount_amount', headerName: 'Discount', width: 80 },
    { field: 'late_fee', headerName: 'Late fee', width: 80 },
    { field: 'paid_amount', headerName: 'Paid', width: 80 },
    { field: 'balance', headerName: 'Balance', width: 80 },
    { field: 'due_date', headerName: 'Due', width: 110 },
    {
      field: 'status',
      headerName: 'Status',
      width: 100,
      renderCell: (p) => (
        <Chip
          label={p.value as string}
          size="small"
          color={p.value === 'paid' ? 'success' : p.value === 'overdue' ? 'error' : 'warning'}
          variant="outlined"
        />
      ),
    },
    {
      field: 'pay',
      headerName: 'Action',
      width: 130,
      renderCell: (p) =>
        canManage && Number(p.row.balance) > 0 ? (
          <Button
            size="small"
            onClick={() => {
              setPayOpen(p.row)
              setPayForm({
                amount: String(p.row.balance),
                mode: 'cash',
                transaction_ref: '',
                cheque_number: '',
                gateway_ref: '',
              })
            }}
          >
            Collect
          </Button>
        ) : null,
    },
  ]

  return (
    <>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField
          size="small"
          label="Search enrollment no."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ minWidth: 200 }}
        />
        <Button size="small" variant="outlined" onClick={load}>Search</Button>
        {canManage && (
          <>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => {
              setForm({ student: '', fee_structure: '', total_amount: '', discount_amount: '0', due_date: new Date().toISOString().slice(0, 10) })
              setOpen(true)
            }}>
              Assign fee
            </Button>
            <Button variant="outlined" onClick={bulkBill}>Quick bill</Button>
            <Button variant="outlined" color="warning" onClick={async () => {
              const { data } = await api.post('/fees/assignments/apply-late-fees/')
              toast.success(`Late fees applied to ${data.updated} account(s)`)
              load()
            }}>Apply late fees</Button>
          </>
        )}
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title="Assign fee to student" onClose={() => setOpen(false)} onSubmit={save} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Student</InputLabel>
          <Select label="Student" value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })}>
            {students.map((s) => (
              <MenuItem key={s.id as number} value={String(s.id)}>
                {(s.enrollment_number as string) || ''} — {(s.full_name as string) || (s.user_name as string)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Fee structure</InputLabel>
          <Select
            label="Fee structure"
            value={form.fee_structure}
            onChange={(e) => {
              const id = e.target.value
              const st = structures.find((s) => String(s.id) === id)
              setForm({ ...form, fee_structure: id, total_amount: st ? String(st.amount) : form.total_amount })
            }}
          >
            {structures.map((s) => (
              <MenuItem key={s.id as number} value={String(s.id)}>
                {String(s.fee_head_name || s.id)} — NPR {String(s.amount)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Total (NPR)" type="number" value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} />
        <TextField fullWidth margin="normal" label="Discount / scholarship (NPR)" type="number" value={form.discount_amount} onChange={(e) => setForm({ ...form, discount_amount: e.target.value })} />
        <TextField fullWidth margin="normal" label="Due date" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} InputLabelProps={{ shrink: true }} />
      </FormDialog>
      <FormDialog open={!!payOpen} title="Record payment" onClose={() => setPayOpen(null)} onSubmit={recordPayment} loading={loading} submitLabel="Record & receipt">
        <TextField fullWidth margin="normal" label="Amount (NPR)" type="number" value={payForm.amount} onChange={(e) => setPayForm({ ...payForm, amount: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Payment mode</InputLabel>
          <Select label="Payment mode" value={payForm.mode} onChange={(e) => setPayForm({ ...payForm, mode: e.target.value })}>
            {PAYMENT_MODES.map((m) => <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Transaction / reference" value={payForm.transaction_ref} onChange={(e) => setPayForm({ ...payForm, transaction_ref: e.target.value })} />
        {(payForm.mode === 'fonepay' || payForm.mode === 'esewa' || payForm.mode === 'khalti') && (
          <TextField fullWidth margin="normal" label="Gateway txn ID (Fonepay ref)" value={payForm.gateway_ref} onChange={(e) => setPayForm({ ...payForm, gateway_ref: e.target.value })} placeholder="e.g. FPY-20260525-001" />
        )}
        {payForm.mode === 'cheque' && (
          <TextField fullWidth margin="normal" label="Cheque number" value={payForm.cheque_number} onChange={(e) => setPayForm({ ...payForm, cheque_number: e.target.value })} />
        )}
        {payForm.mode === 'fonepay' && (
          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Button size="small" variant="outlined" onClick={initiateFonepay} disabled={!paymentsOnlineEnabled}>
              Start Fonepay
            </Button>
            <Button size="small" variant="outlined" color="success" onClick={confirmFonepay}>
              Confirm Fonepay
            </Button>
          </Box>
        )}
        {payForm.mode === 'fonepay' && !paymentsOnlineEnabled && (
          <Typography variant="caption" color="text.secondary">
            Enable feature flag payments_online to start gateway initiation from portal.
          </Typography>
        )}
      </FormDialog>
    </>
  )
}

const PAYMENT_MODES = [
  { value: 'cash', label: 'Cash' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'esewa', label: 'eSewa' },
  { value: 'khalti', label: 'Khalti' },
  { value: 'connect_ips', label: 'Connect IPS' },
  { value: 'fonepay', label: 'Fonepay' },
]

function BillingRunsPanel({ canManage }: { canManage: boolean }) {
  const [rows, setRows] = useState<Row[]>([])
  const [courses, setCourses] = useState<{ id: number; name: string; code: string }[]>([])
  const [batches, setBatches] = useState<{ id: number; name: string }[]>([])
  const [scholarships, setScholarships] = useState<{ id: number; name: string; code: string }[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    run_type: 'batch', course: '', batch: '', semester: '1', due_date: '', default_scholarship: '', apply_scholarship: true, installments: '1', interval_days: '30', notes: '',
  })

  const load = useCallback(() => {
    api.get('/fees/billing-runs/').then((r) => setRows(r.data.results || r.data))
    api.get('/courses/').then((r) => setCourses(r.data.results || r.data))
    api.get('/students/batches/').then((r) => setBatches(r.data.results || r.data))
    api.get('/fees/scholarships/').then((r) => setScholarships(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const execute = async () => {
    setLoading(true)
    try {
      const { data } = await api.post('/fees/billing-runs/execute/', {
        run_type: form.run_type,
        course: form.course ? Number(form.course) : null,
        batch: form.batch ? Number(form.batch) : null,
        semester: form.semester ? Number(form.semester) : null,
        due_date: form.due_date,
        default_scholarship: form.default_scholarship ? Number(form.default_scholarship) : null,
        apply_scholarship: form.apply_scholarship,
        installments: Number(form.installments || 1),
        interval_days: Number(form.interval_days || 30),
        notes: form.notes,
      })
      toast.success(`Billing run #${data.id}: ${data.assignments_created} created, ${data.assignments_skipped} skipped`)
      setOpen(false)
      load()
    } catch {
      toast.error('Billing run failed')
    } finally {
      setLoading(false)
    }
  }

  const columns: GridColDef[] = [
    { field: 'id', headerName: '#', width: 60 },
    { field: 'run_type', headerName: 'Type', width: 90 },
    { field: 'batch_name', headerName: 'Batch', width: 120 },
    { field: 'semester', headerName: 'Sem', width: 60 },
    { field: 'due_date', headerName: 'Due', width: 110 },
    { field: 'assignments_created', headerName: 'Billed', width: 80 },
    { field: 'assignments_skipped', headerName: 'Skipped', width: 80 },
    { field: 'scholarship_name', headerName: 'Scholarship', width: 140 },
    { field: 'created_at', headerName: 'When', width: 160, valueGetter: (_, r) => String(r.created_at || '').slice(0, 16) },
  ]

  return (
    <>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Run semester or batch-wise billing against approved enrollments. Structures must match program, batch, and semester.
      </Typography>
      {canManage && (
        <Button sx={{ mb: 2 }} variant="contained" startIcon={<AddIcon />} onClick={() => {
          setForm({
            run_type: 'batch',
            course: '',
            batch: '',
            semester: '1',
            due_date: new Date(Date.now() + 15 * 86400000).toISOString().slice(0, 10),
            default_scholarship: '',
            apply_scholarship: true,
            installments: '1',
            interval_days: '30',
            notes: '',
          })
          setOpen(true)
        }}>
          Run billing
        </Button>
      )}
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title="Execute billing run" onClose={() => setOpen(false)} onSubmit={execute} loading={loading} maxWidth="sm">
        <FormControl fullWidth margin="normal">
          <InputLabel>Run type</InputLabel>
          <Select label="Run type" value={form.run_type} onChange={(e) => setForm({ ...form, run_type: e.target.value })}>
            <MenuItem value="batch">By batch</MenuItem>
            <MenuItem value="semester">By semester</MenuItem>
            <MenuItem value="manual">Manual (filters)</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Program</InputLabel>
          <Select label="Program" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })}>
            <MenuItem value="">All / any</MenuItem>
            {courses.map((c) => <MenuItem key={c.id} value={String(c.id)}>{c.code} — {c.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Batch</InputLabel>
          <Select label="Batch" value={form.batch} onChange={(e) => setForm({ ...form, batch: e.target.value })}>
            <MenuItem value="">All</MenuItem>
            {batches.map((b) => <MenuItem key={b.id} value={String(b.id)}>{b.name}</MenuItem>)}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Semester" type="number" value={form.semester} onChange={(e) => setForm({ ...form, semester: e.target.value })} />
        <TextField fullWidth margin="normal" label="Due date" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} InputLabelProps={{ shrink: true }} />
        <TextField fullWidth margin="normal" label="Installments" type="number" value={form.installments} onChange={(e) => setForm({ ...form, installments: e.target.value })} />
        <TextField fullWidth margin="normal" label="Interval days between installments" type="number" value={form.interval_days} onChange={(e) => setForm({ ...form, interval_days: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Default scholarship (optional)</InputLabel>
          <Select label="Default scholarship (optional)" value={form.default_scholarship} onChange={(e) => setForm({ ...form, default_scholarship: e.target.value })}>
            <MenuItem value="">None</MenuItem>
            {scholarships.map((s) => <MenuItem key={s.id} value={String(s.id)}>{s.code} — {s.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>Apply scholarship</InputLabel>
          <Select label="Apply scholarship" value={form.apply_scholarship ? 'yes' : 'no'} onChange={(e) => setForm({ ...form, apply_scholarship: e.target.value === 'yes' })}>
            <MenuItem value="yes">Yes — auto discount on new bills</MenuItem>
            <MenuItem value="no">No — bill full amount</MenuItem>
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      </FormDialog>
    </>
  )
}

function PoliciesPanel({ canManage }: { canManage: boolean }) {
  const [latePolicies, setLatePolicies] = useState<Row[]>([])
  const [scholarships, setScholarships] = useState<Row[]>([])
  const [heads, setHeads] = useState<{ id: number; name: string }[]>([])
  const [lateForm, setLateForm] = useState({ name: 'Standard late fee', grace_days: 7, rate_percent: 2, flat_amount: 500 })
  const [schForm, setSchForm] = useState({ code: '', name: '', scholarship_type: 'percent', value: '', fee_head: '' })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/fees/late-fee-policies/').then((r) => setLatePolicies(r.data.results || r.data))
    api.get('/fees/scholarships/').then((r) => setScholarships(r.data.results || r.data))
    api.get('/fees/heads/').then((r) => setHeads(r.data.results || r.data))
  }, [])

  useEffect(() => { load() }, [load])

  const saveLate = async () => {
    setLoading(true)
    try {
      await api.post('/fees/late-fee-policies/', lateForm)
      toast.success('Late fee policy saved')
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  const saveScholarship = async () => {
    setLoading(true)
    try {
      await api.post('/fees/scholarships/', {
        ...schForm,
        value: schForm.value,
        fee_head: schForm.fee_head ? Number(schForm.fee_head) : null,
      })
      toast.success('Scholarship saved')
      setSchForm({ code: '', name: '', scholarship_type: 'percent', value: '', fee_head: '' })
      load()
    } catch {
      toast.error('Save failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Late fee policy</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Applied manually via &quot;Apply late fees&quot; on the ledger. Grace days after due date, then % + flat on outstanding balance.
        </Typography>
        {canManage && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <TextField size="small" label="Name" value={lateForm.name} onChange={(e) => setLateForm({ ...lateForm, name: e.target.value })} />
            <TextField size="small" label="Grace days" type="number" value={lateForm.grace_days} onChange={(e) => setLateForm({ ...lateForm, grace_days: Number(e.target.value) })} />
            <TextField size="small" label="Rate %" type="number" value={lateForm.rate_percent} onChange={(e) => setLateForm({ ...lateForm, rate_percent: Number(e.target.value) })} />
            <TextField size="small" label="Flat NPR" type="number" value={lateForm.flat_amount} onChange={(e) => setLateForm({ ...lateForm, flat_amount: Number(e.target.value) })} />
            <Button variant="outlined" onClick={saveLate} disabled={loading}>Add policy</Button>
          </Box>
        )}
        <DataTable rows={latePolicies} columns={[
          { field: 'name', headerName: 'Policy', flex: 1 },
          { field: 'grace_days', headerName: 'Grace', width: 70 },
          { field: 'rate_percent', headerName: '%', width: 60 },
          { field: 'is_active', headerName: 'Active', width: 80 },
        ]} getRowId={(r) => r.id} autoHeight />
      </Grid>
      <Grid item xs={12} md={6}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>Scholarships</Typography>
        {canManage && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <TextField size="small" label="Code" value={schForm.code} onChange={(e) => setSchForm({ ...schForm, code: e.target.value })} />
            <TextField size="small" label="Name" value={schForm.name} onChange={(e) => setSchForm({ ...schForm, name: e.target.value })} />
            <FormControl size="small">
              <InputLabel>Type</InputLabel>
              <Select label="Type" value={schForm.scholarship_type} onChange={(e) => setSchForm({ ...schForm, scholarship_type: e.target.value })}>
                <MenuItem value="percent">Percentage</MenuItem>
                <MenuItem value="fixed">Fixed NPR</MenuItem>
              </Select>
            </FormControl>
            <TextField size="small" label="Value" type="number" value={schForm.value} onChange={(e) => setSchForm({ ...schForm, value: e.target.value })} />
            <FormControl size="small">
              <InputLabel>Fee head (optional)</InputLabel>
              <Select label="Fee head (optional)" value={schForm.fee_head} onChange={(e) => setSchForm({ ...schForm, fee_head: e.target.value })}>
                <MenuItem value="">Any head</MenuItem>
                {heads.map((h) => <MenuItem key={h.id} value={String(h.id)}>{h.name}</MenuItem>)}
              </Select>
            </FormControl>
            <Button variant="outlined" onClick={saveScholarship} disabled={loading}>Add scholarship</Button>
          </Box>
        )}
        <DataTable rows={scholarships} columns={[
          { field: 'code', headerName: 'Code', width: 100 },
          { field: 'name', headerName: 'Name', flex: 1 },
          { field: 'scholarship_type', headerName: 'Type', width: 90 },
          { field: 'value', headerName: 'Value', width: 80 },
        ]} getRowId={(r) => r.id} autoHeight />
      </Grid>
    </Grid>
  )
}

function PaymentsRegisterPanel() {
  const [rows, setRows] = useState<Row[]>([])
  const [search, setSearch] = useState('')

  const load = useCallback(() => {
    const params: Record<string, string> = {}
    if (search) params.search = search
    api.get('/fees/payments/', { params }).then((r) => setRows(r.data.results || r.data))
  }, [search])

  useEffect(() => { load() }, [load])

  const columns: GridColDef[] = [
    { field: 'receipt_id', headerName: 'Receipt', width: 130 },
    { field: 'created_at', headerName: 'Date', width: 160, valueGetter: (_, row) => String(row.created_at || '').slice(0, 16) },
    { field: 'enrollment_number', headerName: 'Student ID', width: 110 },
    { field: 'student_name', headerName: 'Student', width: 150 },
    { field: 'fee_head_name', headerName: 'Fee head', width: 120 },
    { field: 'amount', headerName: 'NPR', width: 90 },
    { field: 'mode_label', headerName: 'Mode', width: 100 },
    { field: 'gateway_ref', headerName: 'Gateway ref', width: 130 },
    {
      field: 'receipt',
      headerName: 'Receipt',
      width: 90,
      renderCell: (p) => (
        <Button size="small" startIcon={<ReceiptIcon />} onClick={() => window.open(`/api/v1/fees/payments/${p.row.id}/receipt-pdf/`, '_blank')}>
          PDF
        </Button>
      ),
    },
  ]

  return (
    <>
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField size="small" label="Filter (student id)" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Button size="small" variant="outlined" onClick={load}>Refresh</Button>
      </Box>
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
    </>
  )
}

function RefundsPanel({ canManage }: { canManage: boolean }) {
  const [rows, setRows] = useState<Row[]>([])
  const [payments, setPayments] = useState<Row[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const user = useAuthStore((s) => s.user)
  const [form, setForm] = useState({ payment: '', amount: '', reason: '' })

  const load = useCallback(() => {
    api.get('/fees/refunds/').then((r) => setRows(r.data.results || r.data))
    api.get('/fees/payments/').then((r) => setPayments((r.data.results || r.data).slice(0, 100)))
  }, [])

  useEffect(() => { load() }, [load])

  const submit = async () => {
    setLoading(true)
    try {
      await api.post('/fees/refunds/', { payment: Number(form.payment), amount: form.amount, reason: form.reason })
      toast.success('Refund request created')
      setOpen(false)
      setForm({ payment: '', amount: '', reason: '' })
      load()
    } catch {
      toast.error('Unable to create refund request')
    } finally {
      setLoading(false)
    }
  }

  const runAction = async (id: number, action: 'approve' | 'reject' | 'complete') => {
    try {
      await api.post(`/fees/refunds/${id}/${action}/`)
      toast.success(`Refund ${action}d`)
      load()
    } catch {
      toast.error(`Refund ${action} failed`)
    }
  }

  const canApprove = user?.role === 'super_admin' || user?.role === 'admin_staff'
  const columns: GridColDef[] = [
    { field: 'id', headerName: '#', width: 60 },
    { field: 'payment', headerName: 'Payment ID', width: 100 },
    { field: 'amount', headerName: 'Amount', width: 100 },
    { field: 'reason', headerName: 'Reason', flex: 1, minWidth: 220 },
    { field: 'status', headerName: 'Status', width: 100 },
    { field: 'created_at', headerName: 'Requested at', width: 150, valueGetter: (_, r) => String(r.created_at || '').slice(0, 10) },
    {
      field: 'actions',
      headerName: 'Action',
      width: 220,
      renderCell: (p) => canApprove ? (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Button size="small" onClick={() => runAction(Number(p.row.id), 'approve')} disabled={p.row.status !== 'pending'}>Approve</Button>
          <Button size="small" color="error" onClick={() => runAction(Number(p.row.id), 'reject')} disabled={p.row.status !== 'pending'}>Reject</Button>
          <Button size="small" color="success" onClick={() => runAction(Number(p.row.id), 'complete')} disabled={p.row.status !== 'approved'}>Complete</Button>
        </Box>
      ) : null,
    },
  ]

  return (
    <>
      {canManage && (
        <Button sx={{ mb: 2 }} variant="outlined" onClick={() => setOpen(true)}>
          New refund request
        </Button>
      )}
      <DataTable rows={rows} columns={columns} getRowId={(r) => r.id} />
      <FormDialog open={open} title="Create refund request" onClose={() => setOpen(false)} onSubmit={submit} loading={loading}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Payment</InputLabel>
          <Select label="Payment" value={form.payment} onChange={(e) => setForm({ ...form, payment: e.target.value })}>
            {payments.map((p) => (
              <MenuItem key={p.id as number} value={String(p.id)}>
                {String(p.receipt_id)} — {String(p.student_name)} — NPR {String(p.amount)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Amount" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <TextField fullWidth margin="normal" label="Reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} multiline minRows={2} />
      </FormDialog>
    </>
  )
}

export default function FeesPage() {
  const { canCreate, canEdit } = usePermissions()
  const canManage = canCreate('fees') || canEdit('fees')
  const [searchParams, setSearchParams] = useSearchParams()
  const studentParam = searchParams.get('student') || ''
  const [studentLabel, setStudentLabel] = useState('')

  useEffect(() => {
    if (!studentParam) {
      setStudentLabel('')
      return
    }
    api.get('/students/', { params: { search: studentParam } })
      .then((r) => {
        const list = r.data.results || r.data
        const match = list.find((s: { enrollment_number: string }) => s.enrollment_number === studentParam) || list[0]
        if (match) setStudentLabel(`${match.enrollment_number} · ${match.full_name}`)
        else setStudentLabel(studentParam)
      })
      .catch(() => setStudentLabel(studentParam))
  }, [studentParam])

  const clearStudentFilter = () => {
    searchParams.delete('student')
    setSearchParams(searchParams)
  }

  return (
    <>
      <PageHeader
        title={studentParam ? `Fees — ${studentLabel || studentParam}` : 'Fee management'}
        subtitle="Collection desk, student ledger, structures, and accounts summary (NPR)"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Fees' }]}
        action={studentParam ? <Button size="small" onClick={clearStudentFilter}>Clear student filter</Button> : undefined}
      />
      <PageTabs
        tabs={[
          { id: 'summary', label: 'Summary', panel: <SummaryPanel /> },
          { id: 'billing', label: 'Billing runs', panel: <BillingRunsPanel canManage={canManage} /> },
          { id: 'assignments', label: 'Student ledger', panel: <FeeAssignmentsPanel canManage={canManage} enrollmentFilter={studentParam} /> },
          { id: 'payments', label: 'Payments register', panel: <PaymentsRegisterPanel /> },
          { id: 'refunds', label: 'Refund workflow', panel: <RefundsPanel canManage={canManage} /> },
          { id: 'policies', label: 'Scholarships & late fee', panel: <PoliciesPanel canManage={canManage} /> },
          { id: 'structures', label: 'Fee structures', panel: <FeeStructuresPanel canManage={canManage} /> },
          { id: 'heads', label: 'Fee heads', panel: <FeeHeadsPanel canManage={canManage} /> },
        ]}
        defaultTab={studentParam ? 'assignments' : 'summary'}
      />
    </>
  )
}
