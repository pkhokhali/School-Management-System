import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { PermissionMap } from '../config/permissions'
import { SUPER_ADMIN_PERMISSIONS, isSuperAdminRole } from '../config/permissions'

export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  full_name: string
  role: string
  role_label?: string
  must_set_password?: boolean
  permissions?: PermissionMap
}

interface AuthState {
  user: User | null
  permissions: PermissionMap | null
  accessToken: string | null
  refreshToken: string | null
  setAuth: (user: User, access: string, refresh: string) => void
  setTokens: (access: string, refresh: string) => void
  setPermissions: (permissions: PermissionMap) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      permissions: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, access, refresh) => {
        const perms =
          user.permissions ?? (isSuperAdminRole(user.role) ? SUPER_ADMIN_PERMISSIONS : null)
        set({
          user,
          accessToken: access,
          refreshToken: refresh,
          permissions: perms,
        })
      },
      setTokens: (access, refresh) =>
        set({ accessToken: access, refreshToken: refresh }),
      setPermissions: (permissions) => set({ permissions }),
      logout: () => set({ user: null, permissions: null, accessToken: null, refreshToken: null }),
    }),
    { name: 'auth-storage' },
  ),
)
