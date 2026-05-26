from rest_framework.permissions import BasePermission, SAFE_METHODS

from courses.models import TeacherAssignment


class CanManageResults(BasePermission):
    """Read: staff + teacher; write marks: super_admin, admin_staff, teacher."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = request.user.role
        if request.method in SAFE_METHODS:
            return role in ('super_admin', 'admin_staff', 'teacher', 'student', 'parent')
        return role in ('super_admin', 'admin_staff', 'teacher')


class CanManageSubjects(BasePermission):
    """Subject catalog setup — institute admins only."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.role in ('super_admin', 'admin_staff', 'teacher')
        return request.user.role in ('super_admin', 'admin_staff')


def teacher_course_ids(user):
    if user.role in ('super_admin', 'admin_staff'):
        return None
    if user.role == 'teacher':
        return list(
            TeacherAssignment.objects.filter(teacher=user).values_list('course_id', flat=True).distinct()
        )
    return []


def user_may_access_course(user, course_id) -> bool:
    allowed = teacher_course_ids(user)
    if allowed is None:
        return True
    return int(course_id) in allowed
