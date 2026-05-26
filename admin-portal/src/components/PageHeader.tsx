import { Box, Breadcrumbs, Link, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import { ReactNode } from 'react'

type PageHeaderProps = {
  title: string
  subtitle?: string
  action?: ReactNode
  breadcrumbs?: { label: string; to?: string }[]
}

export default function PageHeader({ title, subtitle, action, breadcrumbs }: PageHeaderProps) {
  return (
    <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: 2 }}>
      <Box>
        {breadcrumbs && breadcrumbs.length > 0 && (
          <Breadcrumbs sx={{ mb: 1 }} aria-label="breadcrumb">
            {breadcrumbs.map((b, i) =>
              b.to ? (
                <Link key={i} component={RouterLink} to={b.to} underline="hover" color="text.secondary" variant="body2">
                  {b.label}
                </Link>
              ) : (
                <Typography key={i} color="text.secondary" variant="body2">
                  {b.label}
                </Typography>
              ),
            )}
          </Breadcrumbs>
        )}
        <Typography variant="h4" color="text.primary">
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action}
    </Box>
  )
}
