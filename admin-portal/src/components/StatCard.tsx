import { alpha, Box, Paper, Typography, useTheme } from '@mui/material'
import { ReactNode } from 'react'

type StatCardProps = {
  label: string
  value: string | number
  icon: ReactNode
  color: string
  trend?: string
  trendUp?: boolean
}

export default function StatCard({ label, value, icon, color, trend, trendUp }: StatCardProps) {
  const theme = useTheme()
  const isLight = theme.palette.mode === 'light'

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: isLight ? '0 12px 32px rgba(15,23,42,0.1)' : '0 12px 32px rgba(0,0,0,0.35)',
        },
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: `linear-gradient(135deg, ${alpha(color, 0.2)} 0%, transparent 70%)`,
        }}
      />
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" fontWeight={500} gutterBottom>
            {label}
          </Typography>
          <Typography variant="h4" fontWeight={700} sx={{ fontFamily: '"Outfit", sans-serif' }}>
            {value ?? '—'}
          </Typography>
          {trend && (
            <Typography
              variant="caption"
              sx={{
                mt: 0.5,
                display: 'inline-block',
                color: trendUp ? 'success.main' : 'warning.main',
                fontWeight: 600,
              }}
            >
              {trend}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.75)} 100%)`,
            color: '#fff',
            boxShadow: `0 8px 16px ${alpha(color, 0.35)}`,
          }}
        >
          {icon}
        </Box>
      </Box>
    </Paper>
  )
}
