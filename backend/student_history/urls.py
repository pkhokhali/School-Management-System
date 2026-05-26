from django.urls import path
from .views import StudentTimelineView

urlpatterns = [
    path('<int:student_id>/timeline/', StudentTimelineView.as_view(), name='student-timeline'),
]
