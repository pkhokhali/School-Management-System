from django.conf import settings
from django.db import models


class Course(models.Model):
    class CourseType(models.TextChoices):
        PROGRAM = 'program', 'Degree / Program'
        SHORT_TERM = 'short_term', 'Short Term'
        INTERNSHIP = 'internship', 'Internship'

    class Level(models.TextChoices):
        CERTIFICATE = 'certificate', 'Certificate'
        DIPLOMA = 'diploma', 'Diploma'
        BACHELOR = 'bachelor', 'Bachelor'
        MASTER = 'master', 'Master'
        PHD = 'phd', 'PhD'

    class DeliveryMode(models.TextChoices):
        ON_CAMPUS = 'on_campus', 'On Campus'
        ONLINE = 'online', 'Online'
        HYBRID = 'hybrid', 'Hybrid'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True, blank=True)
    course_type = models.CharField(
        max_length=20, choices=CourseType.choices, default=CourseType.PROGRAM,
    )
    syllabus_pdf = models.FileField(upload_to='syllabi/courses/', blank=True, null=True)
    department = models.ForeignKey(
        'students.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses',
    )
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BACHELOR)
    duration_months = models.PositiveSmallIntegerField(default=12, help_text='Total program length in months')
    duration_years = models.DecimalField(max_digits=3, decimal_places=1, default=4, help_text='Display duration e.g. 4 years')
    total_semesters = models.PositiveSmallIntegerField(default=8)
    credits = models.PositiveSmallIntegerField(default=3)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_enrollment = models.PositiveIntegerField(default=60)
    delivery_mode = models.CharField(max_length=20, choices=DeliveryMode.choices, default=DeliveryMode.ON_CAMPUS)
    description = models.TextField(blank=True)
    learning_outcomes = models.TextField(blank=True, help_text='What students will achieve')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def save(self, *args, **kwargs):
        if not self.code:
            from .services import generate_course_code
            self.code = generate_course_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} — {self.name}'


class CoursePrerequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_for')


class SyllabusFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='syllabi')
    file = models.FileField(upload_to='syllabi/')
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CourseMaterial(models.Model):
    class MaterialType(models.TextChoices):
        NOTE = 'note', 'Note'
        ASSIGNMENT = 'assignment', 'Assignment'
        RECORDING = 'recording', 'Recording'
        VIDEO = 'video', 'Video Link'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MaterialType.choices)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    url = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CourseSubject(models.Model):
    """Teaching subject within a program (course), per semester."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    semester = models.PositiveSmallIntegerField(default=1)
    credit_hours = models.DecimalField(max_digits=4, decimal_places=1, default=3)
    max_internal = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    max_external = models.DecimalField(max_digits=6, decimal_places=2, default=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['semester', 'code']
        unique_together = [('course', 'code')]

    def __str__(self):
        return f'{self.code} — {self.name} (Sem {self.semester})'


class TeacherAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='teachers')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_assignments')
    batch = models.ForeignKey('students.Batch', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = [('course', 'teacher', 'batch')]
