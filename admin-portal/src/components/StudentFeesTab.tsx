import { Fragment, useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  Chip,
  Collapse,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import ReceiptIcon from '@mui/icons-material/Receipt'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import PaymentsIcon from '@mui/icons-material/Payments'
import { toast } from 'sonner'
import FormDialog from './FormDialog'
import api from '../api/client'

type Assignment = {
  id: number
  fee_head_name: string
  course_name?: string
  semester?: number
  scholarship_name?: string
  late_fee?: number
  total_amount: number
  discount_amount: number
  paid_amount: number
  balance: number
  due_date: string
  status: string
}

type Payment = {
  id: number
  amount: number
  mode: string
  receipt_id: string
  created_at: string
}

type Props = {
  studentId: number
  enrollmentNumber: string
  canManage: boolean
}

export default function StudentFeesTab({ studentId, enrollmentNumber, canManage }: Props) {
  const navigate = useNavigate()
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [paymentsByAssignment, setPaymentsByAssignment] = useState<Record<number, Payment[]>>({})
  const [expanded, setExpanded] = useState<Record<number, boolean>>({})
  const [outstanding, setOutstanding] = useState(0)
  const [payOpen, setPayOpen] = useState<Assignment | null>(null)
  const [payForm, setPayForm] = useState({ amount: '', mode: 'cash', transaction_ref: '', cheque_number: '', gateway_ref: '' })
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/fees/assignments/', { params: { student: studentId } }).then((r) => {
      const list = r.data.results || r.data
      setAssignments(list)
      const total = list.reduce((s: number, a: Assignment) => s + Number(a.balance || 0), 0)
      setOutstanding(total)
    })
  }, [studentId])

  useEffect(() => { load() }, [load])

  const loadPayments = async (assignmentId: number) => {
    const r = await api.get('/fees/payments/', { params: { student_fee: assignmentId } })
    setPaymentsByAssignment((prev) => ({ ...prev, [assignmentId]: r.data.results || r.data }))
  }

  const toggleExpand = async (id: number) => {
    const next = !expanded[id]
    setExpanded((e) => ({ ...e, [id]: next }))
    if (next && !paymentsByAssignment[id]) await loadPayments(id)
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
      toast.success(`Payment recorded — ${data.receipt_id}`)
      setPayOpen(null)
      load()
      if (expanded[payOpen.id]) await loadPayments(payOpen.id)
    } catch {
      toast.error('Payment failed')
    } finally {
      setLoading(false)
    }
  }

  const statusColor = (s: string) => (s === 'paid' ? 'success' : s === 'overdue' ? 'error' : 'warning')

  return (
    <Box>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2, alignItems: 'center' }}>
        <Chip
          label={`Outstanding: NPR ${outstanding.toLocaleString()}`}
          color={outstanding > 0 ? 'warning' : 'success'}
          variant="outlined"
        />
        <Button
          size="small"
          variant="outlined"
          startIcon={<PaymentsIcon />}
          onClick={() => navigate(`/fees?student=${encodeURIComponent(enrollmentNumber)}`)}
        >
          View full fees
        </Button>
      </Box>

      {assignments.length === 0 ? (
        <Typography variant="body2" color="text.secondary">No fee assignments for this student.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell width={40} />
              <TableCell>Fee head</TableCell>
              <TableCell>Due</TableCell>
              <TableCell align="right">Balance</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {assignments.map((a) => (
              <Fragment key={a.id}>
                <TableRow>
                  <TableCell>
                    <IconButton size="small" onClick={() => toggleExpand(a.id)}>
                      {expanded[a.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>{a.fee_head_name}</Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {[a.course_name, a.semester ? `Sem ${a.semester}` : null, a.scholarship_name].filter(Boolean).join(' · ')}
                      {Number(a.late_fee) > 0 ? ` · Late NPR ${a.late_fee}` : ''}
                    </Typography>
                  </TableCell>
                  <TableCell>{a.due_date}</TableCell>
                  <TableCell align="right">NPR {Number(a.balance).toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip label={a.status} size="small" color={statusColor(a.status)} variant="outlined" />
                  </TableCell>
                  <TableCell align="right">
                    {canManage && Number(a.balance) > 0 && (
                      <Button size="small" onClick={() => {
                        setPayOpen(a)
                        setPayForm({ amount: String(a.balance), mode: 'cash', transaction_ref: '', cheque_number: '', gateway_ref: '' })
                      }}>
                        Collect
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell colSpan={6} sx={{ py: 0, border: 0 }}>
                    <Collapse in={!!expanded[a.id]}>
                      <Box sx={{ pl: 5, pb: 1 }}>
                        {(paymentsByAssignment[a.id] || []).length === 0 ? (
                          <Typography variant="caption" color="text.secondary">No payments yet</Typography>
                        ) : (
                          (paymentsByAssignment[a.id] || []).map((p) => (
                            <Box key={p.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5 }}>
                              <Typography variant="caption">
                                {String(p.created_at).slice(0, 10)} · NPR {p.amount} · {p.mode} · {p.receipt_id}
                              </Typography>
                              <IconButton
                                size="small"
                                onClick={() => window.open(`/api/v1/fees/payments/${p.id}/receipt-pdf/`, '_blank')}
                              >
                                <ReceiptIcon fontSize="small" />
                              </IconButton>
                            </Box>
                          ))
                        )}
                      </Box>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </Fragment>
            ))}
          </TableBody>
        </Table>
      )}

      <FormDialog open={!!payOpen} title="Record payment" onClose={() => setPayOpen(null)} onSubmit={recordPayment} loading={loading} submitLabel="Record">
        <TextField fullWidth margin="normal" label="Amount (NPR)" type="number" value={payForm.amount} onChange={(e) => setPayForm({ ...payForm, amount: e.target.value })} />
        <FormControl fullWidth margin="normal">
          <InputLabel>Mode</InputLabel>
          <Select label="Mode" value={payForm.mode} onChange={(e) => setPayForm({ ...payForm, mode: e.target.value })}>
            <MenuItem value="cash">Cash</MenuItem>
            <MenuItem value="cheque">Cheque</MenuItem>
            <MenuItem value="esewa">eSewa</MenuItem>
            <MenuItem value="khalti">Khalti</MenuItem>
            <MenuItem value="connect_ips">Connect IPS</MenuItem>
            <MenuItem value="fonepay">Fonepay</MenuItem>
          </Select>
        </FormControl>
        <TextField fullWidth margin="normal" label="Reference" value={payForm.transaction_ref} onChange={(e) => setPayForm({ ...payForm, transaction_ref: e.target.value })} />
        {payForm.mode === 'fonepay' && (
          <TextField fullWidth margin="normal" label="Fonepay txn ID" value={payForm.gateway_ref} onChange={(e) => setPayForm({ ...payForm, gateway_ref: e.target.value })} placeholder="FPY-..." />
        )}
      </FormDialog>
    </Box>
  )
}
