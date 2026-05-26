from django.conf import settings
from django.db import models


class GradePolicy(models.Model):
    name = models.CharField(max_length=100)
    rules = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)


class Exam(models.Model):
    class ExamType(models.TextChoices):
        INTERNAL = 'internal', 'Internal'
        MID_TERM = 'mid_term', 'Mid Term'
        FINAL = 'final', 'Final'

    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=ExamType.choices)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(
        'courses.CourseSubject', on_delete=models.CASCADE, related_name='exams',
        null=True, blank=True,
    )
    term = models.CharField(max_length=50)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    is_published = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'subject', 'exam_type', 'term'],
                condition=models.Q(subject__isnull=False),
                name='unique_exam_per_subject_term',
            ),
        ]


class MarkEntry(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='marks')
    enrollment = models.ForeignKey(
        'enrollment.Enrollment', on_delete=models.SET_NULL, null=True, blank=True, related_name='marks',
    )
    internal_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    external_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grade = models.CharField(max_length=5, blank=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('exam', 'student')]


class ResultApproval(models.Model):
    class Stage(models.TextChoices):
        TEACHER = 'teacher', 'Teacher'
        HOD = 'hod', 'HOD'
        ADMIN = 'admin', 'Admin'
        PUBLISHED = 'published', 'Published'

    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, related_name='approval')
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.TEACHER)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
