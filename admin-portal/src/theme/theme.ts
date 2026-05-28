import { alpha, createTheme, ThemeOptions } from '@mui/material/styles'
import { instituteBrand } from './instituteBrand'

export function buildTheme(mode: 'light' | 'dark') {
  const isLight = mode === 'light'
  const primary = instituteBrand.indigo

  const options: ThemeOptions = {
    palette: {
      mode,
      primary: { main: primary, light: '#818cf8', dark: '#3730a3', contrastText: '#fff' },
      secondary: { main: instituteBrand.navy, light: '#334155', dark: '#0f172a' },
      success: { main: instituteBrand.success },
      warning: { main: '#f59e0b' },
      error: { main: instituteBrand.error },
      info: { main: instituteBrand.info },
      background: {
        default: isLight ? instituteBrand.surface : '#0f1117',
        paper: isLight ? instituteBrand.white : '#1a1d27',
      },
      divider: isLight ? instituteBrand.cardBorder : alpha('#fff', 0.08),
      text: {
        primary: isLight ? instituteBrand.textPrimary : '#f1f5f9',
        secondary: isLight ? instituteBrand.textMuted : '#94a3b8',
      },
    },
    typography: {
      fontFamily: '"DM Sans", system-ui, sans-serif',
      h4: { fontFamily: '"Outfit", sans-serif', fontWeight: 800, letterSpacing: '-0.02em', color: instituteBrand.textPrimary },
      h5: { fontFamily: '"Outfit", sans-serif', fontWeight: 700, letterSpacing: '-0.01em' },
      h6: { fontFamily: '"Outfit", sans-serif', fontWeight: 700 },
      subtitle1: { fontWeight: 500 },
      button: { textTransform: 'none', fontWeight: 700 },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: { backgroundColor: isLight ? instituteBrand.surface : undefined },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            borderRadius: 12,
            border: isLight ? `0.5px solid ${instituteBrand.cardBorder}` : `1px solid ${alpha('#fff', 0.06)}`,
            boxShadow: isLight ? 'none' : undefined,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: { borderRadius: 10, boxShadow: 'none', fontWeight: 700 },
          contained: {
            backgroundColor: primary,
            '&:hover': { backgroundColor: '#3730a3', boxShadow: `0 8px 20px ${alpha(primary, 0.35)}` },
          },
          outlined: {
            borderColor: instituteBrand.cardBorder,
            color: instituteBrand.textPrimary,
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: isLight ? instituteBrand.navy : '#1a1d27',
            color: '#fff',
            borderRight: 'none',
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            margin: '2px 10px',
            color: alpha('#fff', 0.75),
            '&:hover': { backgroundColor: alpha('#fff', 0.08), color: '#fff' },
            '&.Mui-selected': {
              backgroundColor: primary,
              color: '#fff',
              '&:hover': { backgroundColor: '#3730a3' },
              '& .MuiListItemIcon-root': { color: '#fff' },
            },
            '& .MuiListItemIcon-root': { color: alpha('#fff', 0.55), minWidth: 40 },
          },
        },
      },
      MuiListItemText: {
        styleOverrides: {
          primary: { fontWeight: 600, fontSize: '0.875rem' },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isLight ? instituteBrand.white : instituteBrand.navy,
            color: instituteBrand.textPrimary,
            borderBottom: `0.5px solid ${instituteBrand.cardBorder}`,
            boxShadow: 'none',
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: { fontWeight: 700, fontSize: '0.7rem' },
        },
      },
    },
  }

  return createTheme(options)
}
