from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


def resolve_announcement_recipients(announcement):
    """Resolve users by role flags and student filters (department / batch / shift)."""
    from students.models import StudentProfile

    user_ids = set()
    roles = announcement.target_roles or []

    if announcement.target_all_teachers or 'teacher' in roles:
        user_ids.update(
            User.objects.filter(role=User.Role.TEACHER, is_active=True).values_list('pk', flat=True)
        )

    if announcement.target_all_admin_staff or 'admin_staff' in roles:
        user_ids.update(
            User.objects.filter(role=User.Role.ADMIN_STAFF, is_active=True).values_list('pk', flat=True)
        )

    include_students = announcement.target_all_students or 'student' in roles
    has_student_filter = (
        announcement.target_departments.exists()
        or announcement.target_batches.exists()
        or announcement.target_shifts.exists()
    )

    if include_students or has_student_filter:
        profiles = StudentProfile.objects.filter(user__is_active=True)
        if announcement.target_departments.exists():
            profiles = profiles.filter(batch__department__in=announcement.target_departments.all())
        if announcement.target_batches.exists():
            profiles = profiles.filter(batch__in=announcement.target_batches.all())
        if announcement.target_shifts.exists():
            profiles = profiles.filter(batch__shift__in=announcement.target_shifts.all())
        if has_student_filter and not include_students:
            pass
        elif not include_students and not has_student_filter:
            profiles = profiles.none()
        user_ids.update(profiles.values_list('user_id', flat=True))

    return list(User.objects.filter(pk__in=user_ids, is_active=True))


def dispatch_announcement(announcement):
    """Deliver via selected channels: web, mobile (in-app), email, sms (stub)."""
    from notifications.models import NotificationLog

    users = resolve_announcement_recipients(announcement)
    channels = announcement.channels or ['web']

    for user in users:
        for channel in channels:
            if channel in ('web', 'mobile'):
                NotificationLog.objects.create(
                    user=user,
                    title=announcement.title,
                    body=announcement.body[:1000],
                    data={'announcement_id': announcement.id, 'channel': channel},
                )

    if 'email' in channels:
        emails = [u.email for u in users if u.email][:200]
        if emails:
            send_mail(
                subject=announcement.title,
                message=announcement.body[:2000],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=True,
            )

    if 'sms' in channels:
        for user in users:
            if user.phone:
                pass  # Integrate SMS provider (Twilio, etc.)

    return len(users)
