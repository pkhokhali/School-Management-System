import { ThemeProvider, CssBaseline } from '@mui/material'
import { ReactNode, useMemo } from 'react'
import { useUiStore } from '../store/uiStore'
import { buildTheme } from './theme'

export function ThemeProviderWrapper({ children }: { children: ReactNode }) {
  const darkMode = useUiStore((s) => s.darkMode)
  const theme = useMemo(() => buildTheme(darkMode ? 'dark' : 'light'), [darkMode])
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  )
}
