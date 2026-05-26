import uuid

from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)

    def __str__(self):
        return self.name


class Shift(models.Model):
    """Morning / evening / weekend class shifts."""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def timing_label(self):
        if self.start_time and self.end_time:
            return f'{self.start_time.strftime("%H:%M")} – {self.end_time.strftime("%H:%M")}'
        if self.start_time:
            return f'from {self.start_time.strftime("%H:%M")}'
        if self.end_time:
            return f'until {self.end_time.strftime("%H:%M")}'
        return '—'

    def save(self, *args, **kwargs):
        if not self.code:
            base = ''.join(c for c in self.name.upper() if c.isalnum())[:12] or 'SHIFT'
            candidate = base
            n = 1
            while Shift.objects.filter(code=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}{n}'
                n += 1
            self.code = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Batch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='batches')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='batches')
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='batches')
    semester = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_number = models.CharField(max_length=30, unique=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    qr_token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['enrollment_number', 'batch'])]

    def save(self, *args, **kwargs):
        if not self.enrollment_number:
            from .services import generate_enrollment_number
            self.enrollment_number = generate_enrollment_number()
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex
        super().save(*args, **kwargs)


class StudentDocument(models.Model):
    class DocType(models.TextChoices):
        ADMISSION = 'admission', 'Admission Letter'
        MARKSHEET = 'marksheet', 'Marksheet'
        ID_PROOF = 'id_proof', 'ID Proof'
        OTHER = 'other', 'Other'

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DocType.choices, default=DocType.OTHER)
    file = models.FileField(upload_to='student_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
