from django.contrib import admin
from .models import Course, CourseMaterial, CourseSubject, SyllabusFile, TeacherAssignment

admin.site.register(Course)
admin.site.register(CourseSubject)
admin.site.register(SyllabusFile)
admin.site.register(CourseMaterial)
admin.site.register(TeacherAssignment)
