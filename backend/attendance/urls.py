from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceRecordViewSet,
    AttendanceSessionViewSet,
    OfflineSyncView,
    PayrollAttendanceSummaryView,
    QRAttendanceView,
    StudentAttendanceReportView,
)

router = DefaultRouter()
router.register('sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register('records', AttendanceRecordViewSet, basename='attendance-record')
urlpatterns = [
    path('qr-mark/', QRAttendanceView.as_view(), name='qr-attendance'),
    path('offline-sync/', OfflineSyncView.as_view(), name='offline-sync'),
    path('reports/students/', StudentAttendanceReportView.as_view(), name='attendance-student-report'),
    path('payroll-summary/', PayrollAttendanceSummaryView.as_view(), name='attendance-payroll-summary'),
    path('', include(router.urls)),
]
