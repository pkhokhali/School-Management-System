from django.conf import settings
from django.db import models


class BiometricDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    default_course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='biometric_devices',
        help_text='Course register when webhook omits course_id.',
    )
    default_period = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BiometricUserMap(models.Model):
    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, related_name='user_maps')
    device_user_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = [('device', 'device_user_id')]


class WebhookLog(models.Model):
    device_id = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
