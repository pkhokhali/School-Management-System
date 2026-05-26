import { Box, Typography, alpha, useTheme } from '@mui/material'
import { ReactNode } from 'react'

export default function FormSection({ title, children }: { title: string; children: ReactNode }) {
  const theme = useTheme()
  return (
    <Box
      sx={{
        mb: 2,
        p: 2,
        borderRadius: 2,
        bgcolor: alpha(theme.palette.primary.main, 0.04),
        border: `1px solid ${alpha(theme.palette.divider, 0.8)}`,
      }}
    >
      <Typography variant="subtitle2" fontWeight={700} color="primary" sx={{ mb: 1.5 }}>
        {title}
      </Typography>
      {children}
    </Box>
  )
}
