from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BulkEnrollmentCSVView, EnrollmentViewSet

router = DefaultRouter()
router.register('', EnrollmentViewSet, basename='enrollment')
urlpatterns = [
    path('bulk-csv/', BulkEnrollmentCSVView.as_view(), name='bulk-enrollment'),
    path('', include(router.urls)),
]
