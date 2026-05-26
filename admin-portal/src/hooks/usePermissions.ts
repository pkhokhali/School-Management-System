import { useEffect, useMemo } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'
import type { Action, ModuleKey, PermissionMap } from '../config/permissions'
import {
  can as canAction,
  isSuperAdminRole,
  resolvePermissions,
  SUPER_ADMIN_PERMISSIONS,
} from '../config/permissions'

export function usePermissions() {
  const user = useAuthStore((s) => s.user)
  const permissions = useAuthStore((s) => s.permissions)
  const setPermissions = useAuthStore((s) => s.setPermissions)

  const isSuperAdmin = isSuperAdminRole(user?.role)

  const effectivePermissions = useMemo(
    () => resolvePermissions(user?.role, permissions),
    [user?.role, permissions],
  )

  useEffect(() => {
    if (!user) return
    if (isSuperAdmin) {
      setPermissions(SUPER_ADMIN_PERMISSIONS)
      return
    }
    if (!permissions) {
      api.get('/auth/permissions/')
        .then((r) => setPermissions(r.data.permissions))
        .catch(() => {})
    }
  }, [user, permissions, isSuperAdmin, setPermissions])

  const can = (module: ModuleKey, action: Action) =>
    canAction(effectivePermissions, module, action, user?.role)

  return {
    permissions: effectivePermissions,
    role: user?.role,
    roleLabel: user?.role_label,
    isSuperAdmin,
    can,
    canCreate: (m: ModuleKey) => can(m, 'create'),
    canEdit: (m: ModuleKey) => can(m, 'edit'),
    canDelete: (m: ModuleKey) => can(m, 'delete'),
    canViewNav: (m: ModuleKey) => can(m, 'view'),
  }
}
