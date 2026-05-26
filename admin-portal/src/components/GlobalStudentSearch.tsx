import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  TextField,
  Typography,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import api from '../api/client'

type StudentHit = {
  id: number
  full_name: string
  enrollment_number: string
  batch_name?: string
}

export default function GlobalStudentSearch() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<StudentHit[]>([])
  const [loading, setLoading] = useState(false)
  const [highlight, setHighlight] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setOpen(true)
      }
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50)
      setQuery('')
      setResults([])
      setHighlight(0)
    }
  }, [open])

  const search = useCallback((q: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!q.trim()) {
      setResults([])
      return
    }
    debounceRef.current = setTimeout(() => {
      setLoading(true)
      api.get('/students/', { params: { search: q.trim() } })
        .then((r) => {
          setResults(r.data.results || r.data)
          setHighlight(0)
        })
        .catch(() => setResults([]))
        .finally(() => setLoading(false))
    }, 300)
  }, [])

  const selectStudent = (s: StudentHit) => {
    setOpen(false)
    navigate(`/students?open=${s.id}`)
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setHighlight((h) => Math.min(h + 1, Math.max(0, results.length - 1)))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHighlight((h) => Math.max(h - 1, 0))
    } else if (e.key === 'Enter' && results[highlight]) {
      e.preventDefault()
      selectStudent(results[highlight])
    }
  }

  return (
    <>
      <TextField
        size="small"
        placeholder="Search students (Ctrl+K)"
        onClick={() => setOpen(true)}
        onFocus={() => setOpen(true)}
        InputProps={{
          readOnly: true,
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
        sx={{ width: { xs: 160, sm: 220, md: 280 }, cursor: 'pointer' }}
      />
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogContent sx={{ pt: 2 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            placeholder="Search by name or enrollment number…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              search(e.target.value)
            }}
            onKeyDown={onKeyDown}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            ↑↓ navigate · Enter open · Esc close
          </Typography>
          <Box sx={{ mt: 1, minHeight: 120 }}>
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                <CircularProgress size={28} />
              </Box>
            )}
            {!loading && query && results.length === 0 && (
              <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                No students found for &quot;{query}&quot;
              </Typography>
            )}
            {!loading && results.length > 0 && (
              <List dense>
                {results.map((s, i) => (
                  <ListItemButton
                    key={s.id}
                    selected={i === highlight}
                    onClick={() => selectStudent(s)}
                  >
                    <ListItemText
                      primary={s.full_name}
                      secondary={`${s.enrollment_number}${s.batch_name ? ` · ${s.batch_name}` : ''}`}
                    />
                  </ListItemButton>
                ))}
              </List>
            )}
          </Box>
        </DialogContent>
      </Dialog>
    </>
  )
}
