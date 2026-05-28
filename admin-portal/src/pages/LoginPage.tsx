import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  Paper,
  TextField,
  Typography,
  alpha,
  InputAdornment,
  IconButton,
  useTheme,
} from '@mui/material'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined'
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined'
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import api from '../api/client'
import { useAuthStore } from '../store/authStore'
import { instituteBrand, navyGradient } from '../theme/instituteBrand'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const navigate = useNavigate()
  const theme = useTheme()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: 'admin@institute.edu.np', password: 'admin123' },
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      const res = await api.post('/auth/login/', { ...data, client_type: 'web' })
      setAuth(res.data.user, res.data.access, res.data.refresh)
      toast.success('Welcome back!')
      navigate('/')
    } catch {
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const primary = theme.palette.primary.main

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex' }}>
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          flex: 1,
          background: navyGradient,
          color: '#fff',
          flexDirection: 'column',
          justifyContent: 'center',
          px: 8,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: alpha('#fff', 0.06),
            top: -100,
            right: -100,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            width: 300,
            height: 300,
            borderRadius: '50%',
            background: alpha('#fff', 0.04),
            bottom: -80,
            left: -60,
          }}
        />
        <Box sx={{ position: 'relative', zIndex: 1, maxWidth: 420 }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 3,
              bgcolor: alpha('#fff', 0.15),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 3,
            }}
          >
            <SchoolOutlinedIcon sx={{ fontSize: 36 }} />
          </Box>
          <Typography variant="h3" fontWeight={700} sx={{ fontFamily: '"Outfit", sans-serif', mb: 2 }}>
            Manage your institute with clarity
          </Typography>
          <Typography sx={{ opacity: 0.9, fontSize: '1.1rem', lineHeight: 1.7 }}>
            Students, attendance, fees, results, and announcements — unified in one beautiful admin experience.
          </Typography>
          <Box sx={{ display: 'flex', gap: 3, mt: 5 }}>
            {['10K+ Students', 'Real-time analytics', 'Secure access'].map((tag) => (
              <Typography key={tag} variant="body2" sx={{ opacity: 0.85, fontWeight: 500 }}>
                ✓ {tag}
              </Typography>
            ))}
          </Box>
        </Box>
      </Box>

      <Box
        sx={{
          flex: { xs: 1, md: '0 0 480px' },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          bgcolor: 'background.default',
        }}
      >
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, sm: 4 },
            width: '100%',
            maxWidth: 400,
            borderRadius: 4,
            border: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="h5" fontWeight={700} gutterBottom sx={{ fontFamily: '"Outfit", sans-serif' }}>
            Welcome back
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to your institute admin account
          </Typography>
          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              fullWidth
              margin="normal"
              label="Email"
              {...register('email')}
              error={!!errors.email}
              helperText={errors.email?.message}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailOutlinedIcon fontSize="small" color="action" />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              fullWidth
              margin="normal"
              label="Password"
              type={showPass ? 'text' : 'password'}
              {...register('password')}
              error={!!errors.password}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockOutlinedIcon fontSize="small" color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setShowPass(!showPass)} edge="end">
                      {showPass ? <VisibilityOffOutlinedIcon /> : <VisibilityOutlinedIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, py: 1.4, borderRadius: 2 }}
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 3, textAlign: 'center' }}>
            Demo: admin@institute.edu.np / admin123
          </Typography>
        </Paper>
      </Box>
    </Box>
  )
}
