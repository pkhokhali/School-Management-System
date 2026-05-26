from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CalendarEventViewSet, CalendarMonthView, CurrentAcademicYearView, IsWorkingDayView

router = DefaultRouter()
router.register('', CalendarEventViewSet, basename='calendar-event')

urlpatterns = [
    path('calendar/month/', CalendarMonthView.as_view(), name='calendar-month'),
    path('calendar/working-day/', IsWorkingDayView.as_view(), name='calendar-working-day'),
    path('calendar/current-academic-year/', CurrentAcademicYearView.as_view(), name='calendar-current-year'),
    path('', include(router.urls)),
]
