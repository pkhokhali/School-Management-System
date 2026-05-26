from django.conf import settings
from django.db import models


class Announcement(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SCHEDULED = 'scheduled', 'Scheduled'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    class Channel(models.TextChoices):
        SMS = 'sms', 'SMS'
        EMAIL = 'email', 'Email'
        WEB = 'web', 'Web Notification'
        MOBILE = 'mobile', 'Mobile App Notification'

    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    channels = models.JSONField(
        default=list,
        help_text='Delivery channels: sms, email, web, mobile',
    )
    target_roles = models.JSONField(
        default=list,
        help_text='Broad roles when not using granular filters: student, teacher, admin_staff',
    )
    target_all_students = models.BooleanField(default=False)
    target_all_teachers = models.BooleanField(default=False)
    target_all_admin_staff = models.BooleanField(default=False)
    target_departments = models.ManyToManyField(
        'students.Department', blank=True, related_name='announcements',
        help_text='Faculty / department-wise (students in batches under these departments)',
    )
    target_batches = models.ManyToManyField('students.Batch', blank=True, related_name='announcements')
    target_shifts = models.ManyToManyField(
        'students.Shift', blank=True, related_name='announcements',
    )
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    is_important = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    publish_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('announcement', 'user')]
