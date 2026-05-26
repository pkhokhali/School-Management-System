from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsInstituteAdmin, IsTeacherOrAdmin
from courses.models import TeacherAssignment
from students.models import StudentProfile
from .models import AttendanceRecord, AttendanceSession
from .serializers import (
    AttendanceRecordSerializer,
    AttendanceSessionSerializer,
    BulkAttendanceSerializer,
    ClassRegisterInputSerializer,
    OfflineSyncResponseSerializer,
    OfflineSyncSerializer,
    PayrollExportSerializer,
    QRAttendanceSerializer,
)
from .services import (
    get_or_create_register,
    mark_attendance,
    mark_from_qr,
    mark_records_payroll_exported,
    payroll_attendance_summary,
    registers_for_teacher,
    resolve_register,
    student_attendance_report,
    sync_offline_record,
)


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.select_related(
        'batch', 'batch__academic_year', 'course', 'teacher', 'shift',
    ).annotate(marked_count=Count('records'))
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    filterset_fields = ['date', 'batch', 'course', 'period', 'shift']

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date', '-id')
        user = self.request.user
        role = getattr(user, 'role', None)
        if role == 'teacher':
            assignment_q = TeacherAssignment.objects.filter(teacher=user).values_list(
                'batch_id', 'course_id',
            )
            pairs = list(assignment_q)
            if pairs:
                q = Q()
                for batch_id, course_id in pairs:
                    q |= Q(batch_id=batch_id, course_id=course_id)
                qs = qs.filter(q)
            else:
                qs = qs.filter(teacher=user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        session, created = get_or_create_register(
            data['date'],
            data['batch'].pk,
            data['course'].pk,
            period=data.get('period', 1),
            teacher=data.get('teacher') or request.user,
            shift_id=data['shift'].pk if data.get('shift') else None,
        )
        out = AttendanceSessionSerializer(session)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(request=ClassRegisterInputSerializer, responses={200: AttendanceSessionSerializer})
    @action(detail=False, methods=['post'], url_path='ensure')
    def ensure(self, request):
        """Get or create class register for date + batch + course + period."""
        ser = ClassRegisterInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            session, warnings = resolve_register(ser.validated_data, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'Batch or course not found'}, status=status.HTTP_404_NOT_FOUND)
        data = AttendanceSessionSerializer(session).data
        if warnings:
            data['warnings'] = warnings
        return Response(data)

    @action(detail=False, methods=['get'], url_path='my-classes')
    def my_classes(self, request):
        """Teacher: assigned classes today with registers auto-created."""
        day = request.query_params.get('date')
        register_date = date.fromisoformat(day) if day else timezone.localdate()
        sessions = registers_for_teacher(request.user, register_date)
        qs = AttendanceSession.objects.filter(
            pk__in=[s.pk for s in sessions],
        ).select_related('batch', 'course', 'shift', 'teacher').annotate(
            marked_count=Count('records'),
        )
        return Response(AttendanceSessionSerializer(qs, many=True).data)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        'session', 'session__batch', 'session__course', 'student__user',
    )
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    filterset_fields = ['session', 'status', 'needs_review', 'source']

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            session, warnings = resolve_register(data, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'Register not found'}, status=status.HTTP_404_NOT_FOUND)

        results = []
        for item in data['records']:
            student = StudentProfile.objects.get(pk=item['student_id'])
            record, _ = mark_attendance(
                session,
                student,
                item['status'],
                AttendanceRecord.Source.MANUAL,
                request.user,
                item.get('remarks', ''),
            )
            results.append(AttendanceRecordSerializer(record).data)
        payload = {'results': results, 'session_id': session.id}
        if warnings:
            payload['warnings'] = warnings
        return Response(payload)

    @action(detail=True, methods=['post'])
    def resolve_conflict(self, request, pk=None):
        record = self.get_object()
        record.needs_review = False
        record.status = request.data.get('status', record.status)
        record.save()
        return Response(AttendanceRecordSerializer(record).data)


class QRAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    @extend_schema(request=QRAttendanceSerializer, responses={200: AttendanceRecordSerializer})
    def post(self, request):
        serializer = QRAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            session, warnings = resolve_register(data, request.user)
            record, _ = mark_from_qr(
                session,
                data['payload'],
                request.user,
                gps_lat=data.get('gps_lat'),
                gps_lng=data.get('gps_lng'),
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Register not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        resp = AttendanceRecordSerializer(record).data
        resp['session_id'] = session.id
        if warnings:
            resp['warnings'] = warnings
        return Response(resp)


class OfflineSyncView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    @extend_schema(request=OfflineSyncSerializer, responses={200: OfflineSyncResponseSerializer})
    def post(self, request):
        serializer = OfflineSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        synced = []
        failed = []
        for item in serializer.validated_data['records']:
            result = sync_offline_record(item, request.user)
            if result.get('ok'):
                synced.append(result)
            else:
                failed.append(result)
        return Response({
            'synced': synced,
            'failed': failed,
            'synced_ids': [r['record_id'] for r in synced],
        })


class StudentAttendanceReportView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        try:
            from_date = date.fromisoformat(request.query_params['from'])
            to_date = date.fromisoformat(request.query_params['to'])
        except (KeyError, ValueError):
            return Response({'detail': 'from and to dates required (YYYY-MM-DD)'}, status=400)
        batch_id = request.query_params.get('batch')
        course_id = request.query_params.get('course')
        rows = student_attendance_report(
            from_date,
            to_date,
            int(batch_id) if batch_id else None,
            int(course_id) if course_id else None,
        )
        return Response({'from_date': from_date.isoformat(), 'to_date': to_date.isoformat(), 'rows': rows})


class PayrollAttendanceSummaryView(APIView):
    """Payroll foundation: eligible student days and teacher class-days in range."""

    permission_classes = [IsAuthenticated, IsInstituteAdmin]

    def get(self, request):
        try:
            from_date = date.fromisoformat(request.query_params['from'])
            to_date = date.fromisoformat(request.query_params['to'])
        except (KeyError, ValueError):
            return Response({'detail': 'from and to dates required (YYYY-MM-DD)'}, status=400)
        batch_id = request.query_params.get('batch')
        course_id = request.query_params.get('course')
        data = payroll_attendance_summary(
            from_date,
            to_date,
            int(batch_id) if batch_id else None,
            int(course_id) if course_id else None,
        )
        return Response(data)

    @extend_schema(request=PayrollExportSerializer)
    def post(self, request):
        ser = PayrollExportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        from_d = d.get('from_date')
        to_d = d.get('to_date')
        count = mark_records_payroll_exported(
            record_ids=d.get('record_ids'),
            from_date=from_d,
            to_date=to_d,
        )
        return Response({'marked_exported': count})
