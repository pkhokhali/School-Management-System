import { alpha, Box, Paper, Typography, useTheme } from '@mui/material'
import { ReactNode } from 'react'

type ChartCardProps = {
  title: string
  subtitle?: string
  children: ReactNode
  height?: number
  action?: ReactNode
}

export default function ChartCard({ title, subtitle, children, height = 320, action }: ChartCardProps) {
  const theme = useTheme()
  const isLight = theme.palette.mode === 'light'

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        height: '100%',
        background: isLight
          ? `linear-gradient(180deg, ${alpha('#fff', 1)} 0%, ${alpha('#f8fafc', 1)} 100%)`
          : undefined,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box>
          <Typography variant="h6">{title}</Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {action}
      </Box>
      <Box sx={{ height, width: '100%' }}>{children}</Box>
    </Paper>
  )
}
