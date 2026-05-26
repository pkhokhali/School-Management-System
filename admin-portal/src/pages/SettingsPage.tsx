import { useEffect, useState } from 'react'
import { Box, Button, Divider, FormControl, FormControlLabel, InputLabel, MenuItem, Paper, Select, Switch, Typography, alpha } from '@mui/material'
import { toast } from 'sonner'
import PageHeader from '../components/PageHeader'
import api from '../api/client'
import { useFeatureStore } from '../store/featureStore'
import { useAuthStore } from '../store/authStore'

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)
  const { flags, fetchFeatures } = useFeatureStore()
  const [localFlags, setLocalFlags] = useState<Record<string, boolean>>({})
  const [roleChannel, setRoleChannel] = useState<Record<string, { web_portal: boolean; mobile_app: boolean }>>({})

  useEffect(() => { setLocalFlags({ ...flags }) }, [flags])
  useEffect(() => {
    api.get('/institute/').then((r) => setRoleChannel(r.data.role_channel_access || {})).catch(() => {})
  }, [])

  if (user?.role !== 'super_admin') {
    return (
      <>
        <PageHeader title="Settings" subtitle="Institute configuration" />
        <Paper sx={{ p: 3, borderRadius: 3 }} elevation={0}>
          <Typography color="text.secondary">Super admin access required.</Typography>
        </Paper>
      </>
    )
  }

  const toggle = (key: string) => setLocalFlags((f) => ({ ...f, [key]: !f[key] }))

  const save = async () => {
    await api.patch('/admin/features/', { feature_flags: localFlags })
    await api.patch('/admin/role-channel-access/', { role_channel_access: roleChannel })
    await fetchFeatures()
    toast.success('Settings updated')
  }

  return (
    <>
      <PageHeader
        title="Settings"
        subtitle="Enable or disable optional modules for your institute"
        breadcrumbs={[{ label: 'Dashboard', to: '/' }, { label: 'Settings' }]}
        action={
          <Button variant="contained" onClick={save}>
            Save changes
          </Button>
        }
      />
      <Paper elevation={0} sx={{ p: 3, borderRadius: 3, maxWidth: 560 }}>
        <Typography variant="h6" gutterBottom>
          Feature flags
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Tier C modules — turn on when ready for production
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {Object.entries(localFlags).map(([key, val]) => (
            <FormControlLabel
              key={key}
              control={<Switch checked={val} onChange={() => toggle(key)} />}
              label={
                <Typography variant="body2" fontWeight={500} sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  {key}
                </Typography>
              }
              sx={{
                mx: 0,
                px: 1.5,
                py: 0.75,
                borderRadius: 2,
                '&:hover': { bgcolor: (t) => alpha(t.palette.primary.main, 0.04) },
              }}
            />
          ))}
        </Box>
      </Paper>

      <Paper elevation={0} sx={{ p: 3, borderRadius: 3, maxWidth: 560, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Role channel access (Web / Mobile)
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Default access per role. Individual users can still override from User Management.
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {(['student', 'teacher', 'admin_staff', 'parent'] as const).map((role) => (
          <Box key={role} sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1.5, flexWrap: 'wrap' }}>
            <Typography sx={{ width: 140, fontFamily: 'monospace' }}>{role}</Typography>
            <FormControl size="small" sx={{ minWidth: 170 }}>
              <InputLabel>Web portal</InputLabel>
              <Select
                label="Web portal"
                value={roleChannel?.[role]?.web_portal ? 'allow' : 'deny'}
                onChange={(e) =>
                  setRoleChannel((prev) => ({
                    ...prev,
                    [role]: { ...(prev[role] || { web_portal: true, mobile_app: true }), web_portal: e.target.value === 'allow' },
                  }))
                }
              >
                <MenuItem value="allow">Allow</MenuItem>
                <MenuItem value="deny">Deny</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 170 }}>
              <InputLabel>Mobile app</InputLabel>
              <Select
                label="Mobile app"
                value={roleChannel?.[role]?.mobile_app ? 'allow' : 'deny'}
                onChange={(e) =>
                  setRoleChannel((prev) => ({
                    ...prev,
                    [role]: { ...(prev[role] || { web_portal: true, mobile_app: true }), mobile_app: e.target.value === 'allow' },
                  }))
                }
              >
                <MenuItem value="allow">Allow</MenuItem>
                <MenuItem value="deny">Deny</MenuItem>
              </Select>
            </FormControl>
          </Box>
        ))}
        <Typography variant="caption" color="text.secondary">
          Super admin access is always enforced by account status; inactive users cannot access either channel.
        </Typography>
      </Paper>
    </>
  )
}
