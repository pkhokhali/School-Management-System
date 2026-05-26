from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import InstituteSettings


class FeatureRequired(BasePermission):
    """Require a feature flag to be enabled."""

    feature_key = None

    def has_permission(self, request, view):
        key = getattr(view, 'feature_key', None) or self.feature_key
        if not key:
            return True
        return InstituteSettings.is_feature_enabled(key)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class IsInstituteAdmin(BasePermission):
    """Super admin or reception / admin staff."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('super_admin', 'admin_staff')
        )


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('super_admin', 'admin_staff', 'teacher')
        )


class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        roles = getattr(view, 'allowed_roles', None) or self.allowed_roles
        if not roles:
            return True
        return request.user.role in roles


class ReadOnlyOrInstituteAdmin(BasePermission):
    """Teachers and all staff can read; only institute admins can write."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.role in (
                'super_admin', 'admin_staff', 'teacher', 'student', 'parent',
            )
        return request.user.role in ('super_admin', 'admin_staff')
