"""Role-based module access for admin portal."""

from django.conf import settings

ROLE_LABELS = {
    'super_admin': 'Super Admin',
    'admin_staff': 'Reception / Admin Staff',
    'teacher': 'Teacher',
    'student': 'Student',
    'parent': 'Parent',
}

ROLE_CHANNEL_ACCESS = None

# Modules and allowed actions per role
MODULE_ACCESS = {
    'super_admin': {
        'dashboard': ['view'],
        'users': ['view', 'create', 'edit', 'delete'],
        'students': ['view', 'create', 'edit', 'delete'],
        'courses': ['view', 'create', 'edit', 'delete'],
        'enrollment': ['view', 'create', 'edit', 'delete'],
        'attendance': ['view', 'create', 'edit', 'delete'],
        'calendar': ['view', 'create', 'edit', 'delete'],
        'announcements': ['view', 'create', 'edit', 'delete'],
        'fees': ['view', 'create', 'edit', 'delete'],
        'results': ['view', 'create', 'edit', 'delete'],
        'analytics': ['view'],
        'reports': ['view'],
        'settings': ['view', 'edit'],
    },
    'admin_staff': {
        'dashboard': ['view'],
        'users': [],
        'students': ['view', 'create', 'edit'],
        'courses': ['view', 'create', 'edit'],
        'enrollment': ['view', 'create', 'edit'],
        'attendance': ['view', 'create', 'edit'],
        'calendar': ['view', 'create', 'edit'],
        'announcements': ['view', 'create', 'edit'],
        'fees': ['view', 'create', 'edit'],
        'results': ['view', 'create', 'edit'],
        'analytics': ['view'],
        'reports': ['view'],
        'settings': [],
    },
    'teacher': {
        'dashboard': ['view'],
        'users': [],
        'students': ['view'],
        'courses': ['view'],
        'enrollment': ['view'],
        'attendance': ['view', 'create', 'edit'],
        'calendar': ['view'],
        'announcements': ['view'],
        'fees': [],
        'results': ['view', 'create', 'edit'],
        'analytics': [],
        'settings': [],
    },
}

ASSIGNABLE_ROLES = [
    {'value': 'admin_staff', 'label': ROLE_LABELS['admin_staff']},
    {'value': 'teacher', 'label': ROLE_LABELS['teacher']},
    {'value': 'student', 'label': ROLE_LABELS['student']},
    {'value': 'parent', 'label': ROLE_LABELS['parent']},
]


def get_permissions_for_role(role: str) -> dict:
    return MODULE_ACCESS.get(role, {})


def can_access(role: str, module: str, action: str) -> bool:
    perms = MODULE_ACCESS.get(role, {})
    return action in perms.get(module, [])


def get_channel_access_for_role(role: str) -> dict:
    from core.models import InstituteSettings
    solo = InstituteSettings.get_solo()
    defaults = getattr(settings, 'DEFAULT_ROLE_CHANNEL_ACCESS', {})
    configured = solo.role_channel_access or {}
    flags = {**defaults, **configured}
    return flags.get(role, {'web_portal': False, 'mobile_app': False})
