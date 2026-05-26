import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
} from '@mui/material'
import { ReactNode } from 'react'

type FormDialogProps = {
  open: boolean
  title: string
  onClose: () => void
  onSubmit: () => void
  loading?: boolean
  submitLabel?: string
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg'
  children: ReactNode
}

export default function FormDialog({
  open,
  title,
  onClose,
  onSubmit,
  loading,
  submitLabel = 'Save',
  maxWidth = 'sm',
  children,
}: FormDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth={maxWidth} fullWidth>
      <DialogTitle sx={{ fontFamily: '"Outfit", sans-serif', fontWeight: 600 }}>
        {title}
      </DialogTitle>
      <DialogContent dividers>
        <Box component="form" id="crud-form" onSubmit={(e) => { e.preventDefault(); onSubmit() }}>
          {children}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" form="crud-form" variant="contained" disabled={loading}>
          {loading ? 'Saving…' : submitLabel}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
