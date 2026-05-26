from django.conf import settings
from django.db import models


class AttendanceSession(models.Model):
    """
    Daily class register: one sheet per date + batch + course + period.
    (UX label: "class register" — not a timetable lecture slot by itself.)
    """

    date = models.DateField(db_index=True)
    batch = models.ForeignKey('students.Batch', on_delete=models.CASCADE, related_name='attendance_sessions')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='attendance_sessions')
    period = models.PositiveSmallIntegerField(
        default=1,
        help_text='Period number when the same course meets more than once per day (1, 2, …).',
    )
    shift = models.ForeignKey(
        'students.Shift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_sessions',
    )
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('date', 'batch', 'course', 'period')]
        indexes = [models.Index(fields=['date', 'batch']), models.Index(fields=['date', 'course'])]

    def __str__(self):
        return f'{self.date} · {self.batch} · {self.course} (P{self.period})'


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'

    class Source(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        QR = 'qr', 'QR Scan'
        OFFLINE = 'offline', 'Offline sync'
        BIOMETRIC = 'biometric', 'Biometric'

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=Status.choices)
    remarks = models.TextField(blank=True)
    source = models.CharField(max_length=15, choices=Source.choices, default=Source.MANUAL)
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    needs_review = models.BooleanField(default=False)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    payroll_exported_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set when this row has been included in a payroll run export.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('session', 'student')]
        indexes = [models.Index(fields=['student', 'session'])]

    @property
    def is_payroll_eligible(self):
        return self.status in (self.Status.PRESENT, self.Status.LATE)
