from django.contrib.auth import get_user_model
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, parsers, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from core.openapi import DetailResponseSerializer
from core.permissions import IsInstituteAdmin, IsSuperAdmin, ReadOnlyOrInstituteAdmin
from .models import AcademicYear, Batch, Department, Shift, StudentDocument, StudentProfile
from .serializers import (
    AcademicYearSerializer,
    BatchSerializer,
    DepartmentSerializer,
    ShiftSerializer,
    StudentDocumentSerializer,
    StudentProfileSerializer,
    StudentRegisterSerializer,
    StudentWriteSerializer,
)
from .services import generate_id_card_response, generate_qr_image, generate_qr_payload

UserModel = get_user_model()


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('name')
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all().order_by('-start_date')
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        year = self.get_object()
        year.is_current = True
        year.save()
        return Response(AcademicYearSerializer(year).data)


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.select_related('department', 'academic_year', 'shift')
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['department', 'academic_year']


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related('user', 'batch', 'batch__shift').prefetch_related('documents')
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['batch']
    search_fields = ['enrollment_number', 'user__email', 'user__first_name', 'user__last_name']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return StudentWriteSerializer
        return StudentProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.Role.SUPER_ADMIN, User.Role.ADMIN_STAFF):
            return self.queryset
        if user.role == User.Role.STUDENT:
            return self.queryset.filter(user=user)
        if user.role == User.Role.TEACHER:
            return self.queryset
        return self.queryset.none()

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        student = self.get_object()
        return Response({'payload': generate_qr_payload(student)})

    @action(detail=True, methods=['get'])
    def qr_image(self, request, pk=None):
        student = self.get_object()
        return HttpResponse(generate_qr_image(student), content_type='image/png')

    @action(detail=True, methods=['get'])
    def id_card(self, request, pk=None):
        student = self.get_object()
        return generate_id_card_response(student)

    @action(detail=True, methods=['post'])
    def assign_batch(self, request, pk=None):
        student = self.get_object()
        batch_id = request.data.get('batch_id')
        if not batch_id:
            return Response({'detail': 'batch_id required'}, status=status.HTTP_400_BAD_REQUEST)
        student.batch_id = batch_id
        student.save(update_fields=['batch'])
        return Response(StudentProfileSerializer(student).data)

    @action(detail=True, methods=['post'], url_path='upload-avatar')
    def upload_avatar(self, request, pk=None):
        student = self.get_object()
        if request.user.role == User.Role.STUDENT and student.user_id != request.user.id:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response({'detail': 'avatar file required'}, status=status.HTTP_400_BAD_REQUEST)
        student.user.avatar = avatar
        student.user.save(update_fields=['avatar'])
        return Response(StudentProfileSerializer(student, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='upload-document')
    def upload_document(self, request, pk=None):
        student = self.get_object()
        serializer = StudentDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentRegisterView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=StudentRegisterSerializer, responses={201: StudentProfileSerializer})
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if UserModel.objects.filter(email=data['email']).exists():
            return Response({'detail': 'Email exists'}, status=status.HTTP_409_CONFLICT)
        user = UserModel.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone', ''),
            role=User.Role.STUDENT,
            address=data.get('address', {}),
        )
        profile = StudentProfile.objects.create(
            user=user,
            date_of_birth=data.get('date_of_birth'),
            batch_id=data.get('batch_id'),
            guardian_name=data.get('guardian_name', ''),
            guardian_phone=data.get('guardian_phone', ''),
            guardian_email=data.get('guardian_email', ''),
            guardian_relation=data.get('guardian_relation', ''),
        )
        return Response(StudentProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


QRResolveRequestSerializer = inline_serializer(
    'QRResolveRequest',
    fields={'payload': serializers.CharField()},
)


class QRResolveView(APIView):
    """Resolve QR scan payload to student."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=QRResolveRequestSerializer,
        responses={200: StudentProfileSerializer, 400: DetailResponseSerializer, 404: DetailResponseSerializer},
    )
    def post(self, request):
        payload = request.data.get('payload', '')
        try:
            from .services import resolve_student_from_qr_payload

            student = resolve_student_from_qr_payload(payload)
            student = StudentProfile.objects.select_related('user', 'batch').get(pk=student.pk)
        except ValueError as exc:
            detail = str(exc)
            code = status.HTTP_404_NOT_FOUND if 'not found' in detail.lower() else status.HTTP_400_BAD_REQUEST
            return Response({'detail': detail}, status=code)
        return Response(StudentProfileSerializer(student).data)
