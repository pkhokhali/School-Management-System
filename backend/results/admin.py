from django.contrib import admin
from .models import Exam, GradePolicy, MarkEntry, ResultApproval
for m in [GradePolicy, Exam, MarkEntry, ResultApproval]:
    admin.site.register(m)
