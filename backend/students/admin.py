from django.contrib import admin
from .models import AcademicYear, Batch, Department, Shift, StudentDocument, StudentProfile

admin.site.register(Shift)
admin.site.register(Department)
admin.site.register(AcademicYear)
admin.site.register(Batch)
admin.site.register(StudentProfile)
admin.site.register(StudentDocument)
