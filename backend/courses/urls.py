from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    CourseMaterialViewSet,
    CourseSubjectViewSet,
    SyllabusFileViewSet,
    TeacherAssignmentViewSet,
)

router = DefaultRouter()
# Subjects use explicit paths below (not router) to avoid clash with CourseViewSet pk='subjects'.
router.register('materials', CourseMaterialViewSet, basename='material')
router.register('syllabi', SyllabusFileViewSet, basename='syllabus')
router.register('teacher-assignments', TeacherAssignmentViewSet, basename='teacher-assignment')
router.register('', CourseViewSet, basename='course')

urlpatterns = [
    # Explicit list routes so POST /courses/subjects/ never hits CourseViewSet detail.
    path(
        'subjects/',
        CourseSubjectViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='course-subject-list',
    ),
    path(
        'subjects/<int:pk>/',
        CourseSubjectViewSet.as_view({
            'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
        }),
        name='course-subject-detail',
    ),
    path('', include(router.urls)),
]
