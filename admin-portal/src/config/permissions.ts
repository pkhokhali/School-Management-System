export type ModuleKey =
  | 'dashboard'
  | 'users'
  | 'students'
  | 'courses'
  | 'enrollment'
  | 'attendance'
  | 'calendar'
  | 'announcements'
  | 'fees'
  | 'results'
  | 'analytics'
  | 'reports'
  | 'settings'

export type Action = 'view' | 'create' | 'edit' | 'delete'

export type PermissionMap = Partial<Record<ModuleKey, Action[]>>

const ALL_ACTIONS: Action[] = ['view', 'create', 'edit', 'delete']

/** Full access — used when role is super_admin or permissions not yet loaded from API */
export const SUPER_ADMIN_PERMISSIONS: PermissionMap = {
  dashboard: ['view'],
  users: ALL_ACTIONS,
  students: ALL_ACTIONS,
  courses: ALL_ACTIONS,
  enrollment: ALL_ACTIONS,
  attendance: ALL_ACTIONS,
  calendar: ALL_ACTIONS,
  announcements: ALL_ACTIONS,
  fees: ALL_ACTIONS,
  results: ALL_ACTIONS,
  analytics: ['view'],
  reports: ['view'],
  settings: ['view', 'edit'],
}

export const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Admin',
  admin_staff: 'Reception / Admin Staff',
  teacher: 'Teacher',
  student: 'Student',
  parent: 'Parent',
}

export function isSuperAdminRole(role?: string | null): boolean {
  return role === 'super_admin'
}

export function resolvePermissions(
  role: string | undefined | null,
  permissions: PermissionMap | null | undefined,
): PermissionMap | undefined {
  if (isSuperAdminRole(role)) return SUPER_ADMIN_PERMISSIONS
  return permissions ?? undefined
}

export function can(
  permissions: PermissionMap | undefined,
  module: ModuleKey,
  action: Action,
  role?: string | null,
): boolean {
  const effective = resolvePermissions(role ?? null, permissions)
  if (!effective) return false
  return (effective[module] ?? []).includes(action)
}

export function canViewNav(
  permissions: PermissionMap | undefined,
  module: ModuleKey,
  role?: string | null,
): boolean {
  return can(permissions, module, 'view', role)
}
