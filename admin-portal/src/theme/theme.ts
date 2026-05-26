import { alpha, createTheme, ThemeOptions } from '@mui/material/styles'

const brand = {
  50: '#eef4ff',
  100: '#d9e6ff',
  200: '#bcd4ff',
  300: '#8eb8ff',
  400: '#5990ff',
  500: '#3366ff',
  600: '#1a44f5',
  700: '#1535e1',
  800: '#182db6',
  900: '#192b8f',
}

const accent = {
  main: '#7c3aed',
  light: '#a78bfa',
  dark: '#5b21b6',
}

export function buildTheme(mode: 'light' | 'dark') {
  const isLight = mode === 'light'

  const options: ThemeOptions = {
    palette: {
      mode,
      primary: { main: brand[600], light: brand[400], dark: brand[800], contrastText: '#fff' },
      secondary: accent,
      success: { main: '#10b981' },
      warning: { main: '#f59e0b' },
      error: { main: '#ef4444' },
      info: { main: '#0ea5e9' },
      background: {
        default: isLight ? '#f4f6fb' : '#0f1117',
        paper: isLight ? '#ffffff' : '#1a1d27',
      },
      divider: isLight ? alpha('#1e293b', 0.08) : alpha('#fff', 0.08),
      text: {
        primary: isLight ? '#0f172a' : '#f1f5f9',
        secondary: isLight ? '#64748b' : '#94a3b8',
      },
    },
    typography: {
      fontFamily: '"DM Sans", system-ui, sans-serif',
      h4: { fontFamily: '"Outfit", sans-serif', fontWeight: 700, letterSpacing: '-0.02em' },
      h5: { fontFamily: '"Outfit", sans-serif', fontWeight: 600, letterSpacing: '-0.01em' },
      h6: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
      subtitle1: { fontWeight: 500 },
      button: { textTransform: 'none', fontWeight: 600 },
    },
    shape: { borderRadius: 14 },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarColor: isLight ? '#cbd5e1 transparent' : '#334155 transparent',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            border: isLight ? `1px solid ${alpha('#1e293b', 0.06)}` : `1px solid ${alpha('#fff', 0.06)}`,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: { borderRadius: 10, boxShadow: 'none' },
          contained: {
            background: `linear-gradient(135deg, ${brand[600]} 0%, ${brand[500]} 100%)`,
            '&:hover': {
              background: `linear-gradient(135deg, ${brand[700]} 0%, ${brand[600]} 100%)`,
              boxShadow: `0 8px 20px ${alpha(brand[600], 0.35)}`,
            },
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: isLight ? `1px solid ${alpha('#1e293b', 0.06)}` : `1px solid ${alpha('#fff', 0.06)}`,
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            margin: '2px 8px',
            '&.Mui-selected': {
              background: isLight
                ? `linear-gradient(135deg, ${alpha(brand[600], 0.12)} 0%, ${alpha(brand[400], 0.08)} 100%)`
                : alpha(brand[400], 0.15),
              '&:hover': { background: alpha(brand[600], 0.18) },
            },
          },
        },
      },
    },
  }

  return createTheme(options)
}

export { brand, accent }
