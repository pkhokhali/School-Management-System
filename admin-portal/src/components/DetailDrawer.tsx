import { Box, Drawer, IconButton, Typography, Divider } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { ReactNode } from 'react'

type DetailDrawerProps = {
  open: boolean
  onClose: () => void
  title: string
  subtitle?: string
  width?: number
  children: ReactNode
  actions?: ReactNode
}

export default function DetailDrawer({
  open,
  onClose,
  title,
  subtitle,
  width = 480,
  children,
  actions,
}: DetailDrawerProps) {
  return (
    <Drawer anchor="right" open={open} onClose={onClose} PaperProps={{ sx: { width: { xs: '100%', sm: width } } }}>
      <Box sx={{ p: 2.5, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h6" fontWeight={700}>{title}</Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>
      {actions && (
        <>
          <Box sx={{ px: 2.5, pb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>{actions}</Box>
          <Divider />
        </>
      )}
      <Box sx={{ p: 2.5, overflowY: 'auto', flex: 1 }}>{children}</Box>
    </Drawer>
  )
}
