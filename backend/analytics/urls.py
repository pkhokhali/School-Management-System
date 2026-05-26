from django.urls import path
from .views import AttendanceTrendView, AtRiskStudentsView, BIReportsView, DashboardAnalyticsView

urlpatterns = [
    path('dashboard/', DashboardAnalyticsView.as_view(), name='dashboard'),
    path('reports/', BIReportsView.as_view(), name='bi-reports'),
    path('attendance-trend/', AttendanceTrendView.as_view(), name='attendance-trend'),
    path('at-risk/', AtRiskStudentsView.as_view(), name='at-risk'),
]
