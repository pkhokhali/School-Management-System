from django.conf import settings
from django.db import models


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        PUBLIC_HOLIDAY = 'public_holiday', 'Public holiday'
        HOLIDAY = 'holiday', 'Institute holiday'
        TERM_BREAK = 'term_break', 'Term break'
        EXAM = 'exam', 'Exam period'
        EVENT = 'event', 'Academic / cultural event'
        ADMISSION = 'admission', 'Admission'
        MEETING = 'meeting', 'Meeting / assembly'

    academic_year = models.ForeignKey(
        'students.AcademicYear',
        on_delete=models.CASCADE,
        related_name='calendar_events',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    google_calendar_id = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_events_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'title']
        indexes = [
            models.Index(fields=['academic_year', 'start_date']),
            models.Index(fields=['event_type', 'start_date']),
        ]

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            self.end_date = self.start_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.start_date} – {self.end_date})'

    @property
    def is_holiday_type(self):
        return self.event_type in (
            self.EventType.PUBLIC_HOLIDAY,
            self.EventType.HOLIDAY,
            self.EventType.TERM_BREAK,
        )
