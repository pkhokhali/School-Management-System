from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    def __init__(self, roles=None):
        self.roles = roles or []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        roles = getattr(view, 'allowed_roles', self.roles)
        return request.user.role in roles
