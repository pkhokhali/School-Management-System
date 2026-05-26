from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task
def publish_scheduled_announcements():
    from .models import Announcement
    now = timezone.now()
    qs = Announcement.objects.filter(
        status=Announcement.Status.SCHEDULED,
        publish_at__lte=now,
    )
    for ann in qs:
        ann.status = Announcement.Status.PUBLISHED
        ann.published_at = now
        ann.save(update_fields=['status', 'published_at'])


@shared_task
def send_announcement_email(announcement_id):
    from .models import Announcement
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        ann = Announcement.objects.get(pk=announcement_id)
    except Announcement.DoesNotExist:
        return
    users = User.objects.filter(is_active=True)
    if ann.target_roles:
        users = users.filter(role__in=ann.target_roles)
    emails = list(users.values_list('email', flat=True)[:100])
    if emails:
        send_mail(
            subject=ann.title,
            message=ann.body[:500],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
