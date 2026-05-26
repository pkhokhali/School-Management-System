from django.conf import settings
from django.db import models


class InstituteSettings(models.Model):
    """Singleton institute configuration."""

    name = models.CharField(max_length=255, default='Educational Institute')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='institute/', blank=True, null=True)
    feature_flags = models.JSONField(default=dict)
    role_channel_access = models.JSONField(
        default=dict,
        help_text='Role channel defaults. Example: {"student":{"web_portal":true,"mobile_app":true}}',
    )
    campus_geofence = models.JSONField(
        default=dict,
        help_text='{"type":"radius","lat":27.7,"lng":85.3,"radius_m":500}',
    )
    late_fee_rate_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Institute settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        if not obj.feature_flags:
            obj.feature_flags = settings.DEFAULT_FEATURE_FLAGS.copy()
            obj.save(update_fields=['feature_flags'])
        if not obj.role_channel_access:
            obj.role_channel_access = getattr(settings, 'DEFAULT_ROLE_CHANNEL_ACCESS', {})
            obj.save(update_fields=['role_channel_access'])
        return obj

    @classmethod
    def is_feature_enabled(cls, key: str) -> bool:
        flags = cls.get_solo().feature_flags
        defaults = settings.DEFAULT_FEATURE_FLAGS
        return flags.get(key, defaults.get(key, False))


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']


class DataDeletionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
