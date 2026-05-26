from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsInstituteAdmin, ReadOnlyOrInstituteAdmin
from results.permissions import CanManageSubjects

from .models import Course, CourseMaterial, CourseSubject, SyllabusFile, TeacherAssignment
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    CourseMaterialSerializer,
    CourseSerializer,
    CourseSubjectSerializer,
    SyllabusFileSerializer,
    TeacherAssignmentSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """Program catalog. Numeric pk only — avoids shadowing /courses/subjects/ etc."""

    lookup_value_regex = r'\d+'
    queryset = Course.objects.select_related('department').prefetch_related('teachers', 'materials')
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['is_active', 'department', 'level', 'delivery_mode', 'course_type']
    search_fields = ['name', 'code', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    @action(detail=True, methods=['get'])
    def full_detail(self, request, pk=None):
        course = self.get_object()
        return Response(CourseDetailSerializer(course, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='upload-syllabus')
    def upload_syllabus(self, request, pk=None):
        course = self.get_object()
        pdf = request.FILES.get('syllabus_pdf') or request.FILES.get('file')
        if not pdf:
            return Response({'detail': 'syllabus_pdf file required'}, status=status.HTTP_400_BAD_REQUEST)
        course.syllabus_pdf = pdf
        course.save(update_fields=['syllabus_pdf'])
        serializer = self.get_serializer(course)
        return Response(serializer.data)


class SyllabusFileViewSet(viewsets.ModelViewSet):
    queryset = SyllabusFile.objects.select_related('course')
    serializer_class = SyllabusFileSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    filterset_fields = ['course']


class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.select_related('course')
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['course', 'material_type']


class CourseSubjectViewSet(viewsets.ModelViewSet):
    queryset = CourseSubject.objects.select_related('course')
    serializer_class = CourseSubjectSerializer
    permission_classes = [IsAuthenticated, CanManageSubjects]
    filterset_fields = ['course', 'semester', 'is_active']
    search_fields = ['name', 'code']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'teacher':
            from results.permissions import teacher_course_ids
            ids = teacher_course_ids(user)
            if ids is not None:
                qs = qs.filter(course_id__in=ids)
        return qs


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherAssignment.objects.select_related('course', 'teacher', 'batch')
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['course', 'teacher', 'batch']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'teacher':
            return qs.filter(teacher=user)
        return qs
