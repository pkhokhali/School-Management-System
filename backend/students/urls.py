from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    BatchViewSet,
    DepartmentViewSet,
    ShiftViewSet,
    QRResolveView,
    StudentProfileViewSet,
    StudentRegisterView,
)

router = DefaultRouter()
router.register('shifts', ShiftViewSet, basename='shift')
router.register('departments', DepartmentViewSet, basename='department')
router.register('academic-years', AcademicYearViewSet, basename='academic-year')
router.register('batches', BatchViewSet, basename='batch')
router.register('', StudentProfileViewSet, basename='student')

urlpatterns = [
    path('register/', StudentRegisterView.as_view(), name='student-register'),
    path('qr/resolve/', QRResolveView.as_view(), name='qr-resolve'),
    path('', include(router.urls)),
]
