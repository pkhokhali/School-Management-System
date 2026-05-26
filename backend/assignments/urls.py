from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AssignmentSubmissionViewSet, AssignmentViewSet

router = DefaultRouter()
router.register('submissions', AssignmentSubmissionViewSet, basename='submission')
router.register('', AssignmentViewSet, basename='assignment')
urlpatterns = [path('', include(router.urls))]
