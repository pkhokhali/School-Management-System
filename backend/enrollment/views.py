import csv
import io

from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from core.permissions import IsInstituteAdmin, ReadOnlyOrInstituteAdmin
from students.models import StudentProfile
from courses.models import Course
from .models import Enrollment
from .serializers import EnrollmentSerializer
from .services import approve_enrollment, certificate_pdf_response, log_status_change


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student__user', 'course', 'batch').prefetch_related('history')
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['status', 'course', 'batch', 'student']

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.Role.SUPER_ADMIN, User.Role.ADMIN_STAFF):
            return self.queryset
        if user.role == User.Role.STUDENT and hasattr(user, 'student_profile'):
            return self.queryset.filter(student=user.student_profile)
        return self.queryset.none()

    def perform_create(self, serializer):
        enrollment = serializer.save()
        log_status_change(enrollment, enrollment.status, self.request.user, 'Created')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        enrollment = self.get_object()
        approve_enrollment(enrollment, request.user)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.REJECTED
        enrollment.save()
        log_status_change(enrollment, enrollment.status, request.user, request.data.get('note', ''))
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = Enrollment.Status.DROPPED
        enrollment.drop_reason = request.data.get('reason', '')
        enrollment.dropped_at = timezone.now()
        enrollment.save()
        log_status_change(enrollment, enrollment.status, request.user, enrollment.drop_reason)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=['get'])
    def certificate(self, request, pk=None):
        return certificate_pdf_response(self.get_object())


BulkEnrollmentCSVSerializer = inline_serializer(
    'BulkEnrollmentCSV',
    fields={'file': serializers.FileField()},
)
BulkEnrollmentCSVResponseSerializer = inline_serializer(
    'BulkEnrollmentCSVResponse',
    fields={'created': serializers.IntegerField()},
)


class BulkEnrollmentCSVView(APIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]

    @extend_schema(
        request=BulkEnrollmentCSVSerializer,
        responses={200: BulkEnrollmentCSVResponseSerializer},
    )
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'CSV file required'}, status=status.HTTP_400_BAD_REQUEST)
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = 0
        for row in reader:
            try:
                student = StudentProfile.objects.get(enrollment_number=row['enrollment_number'])
                course = Course.objects.get(code=row['course_code'])
                Enrollment.objects.get_or_create(
                    student=student, course=course,
                    defaults={'batch_id': row.get('batch_id') or None, 'status': Enrollment.Status.PENDING},
                )
                created += 1
            except Exception:
                continue
        return Response({'created': created})
