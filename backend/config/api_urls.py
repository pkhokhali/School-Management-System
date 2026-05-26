from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('enrollment/', include('enrollment.urls')),
    path('announcements/', include('announcements.urls')),
    path('attendance/', include('attendance.urls')),
    path('biometric/', include('biometric_integration.urls')),
    path('fees/', include('fees.urls')),
    path('results/', include('results.urls')),
    path('student-history/', include('student_history.urls')),
    path('analytics/', include('analytics.urls')),
    path('communication/', include('communication.urls')),
    path('library/', include('library.urls')),
    path('leave/', include('leave.urls')),
    path('events/', include('events.urls')),
    path('assignments/', include('assignments.urls')),
]
