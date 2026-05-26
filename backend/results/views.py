from django.db.models import Q
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from core.mixins import FeatureFlagViewMixin
from core.services.pdf import generate_marksheet_pdf
from enrollment.models import Enrollment
from .mark_sheet import build_mark_sheet, save_mark_sheet
from .models import Exam, GradePolicy, MarkEntry, ResultApproval
from .permissions import CanManageResults, teacher_course_ids, user_may_access_course
from .serializers import (
    ExamSerializer,
    ExamSessionSerializer,
    GradePolicySerializer,
    MarkEntrySerializer,
    MarkSheetQuerySerializer,
    MarkSheetSaveSerializer,
    ResultApprovalSerializer,
)
from .services import calculate_grade, calculate_gpa


class ResultsFeatureMixin(FeatureFlagViewMixin):
    feature_key = 'results_publishing'


class ExamViewSet(ResultsFeatureMixin, viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('course', 'subject').prefetch_related('approval', 'marks')
    permission_classes = [IsAuthenticated, CanManageResults]
    filterset_fields = ['course', 'subject', 'exam_type', 'term', 'is_published']

    def get_serializer_class(self):
        if self.action in ('list', 'sessions'):
            return ExamSessionSerializer
        return ExamSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.STUDENT:
            return qs.filter(is_published=True)
        ids = teacher_course_ids(user)
        if ids is not None:
            qs = qs.filter(course_id__in=ids)
        pending = self.request.query_params.get('pending_approval')
        if pending == 'true':
            qs = qs.filter(is_published=False)
        return qs

    @action(detail=False, methods=['get'], url_path='sessions')
    def sessions(self, request):
        """Exams with approval state for publish workflow UI."""
        qs = self.filter_queryset(self.get_queryset())
        return Response(ExamSessionSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'], url_path='submit-approval')
    def submit_approval(self, request, pk=None):
        exam = self.get_object()
        if exam.marks.count() == 0:
            return Response({'detail': 'Enter marks before submitting for approval.'}, status=status.HTTP_400_BAD_REQUEST)
        approval, created = ResultApproval.objects.get_or_create(
            exam=exam,
            defaults={'stage': ResultApproval.Stage.TEACHER},
        )
        if not created and approval.stage == ResultApproval.Stage.PUBLISHED:
            return Response({'detail': 'Already published.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ResultApprovalSerializer(approval).data)


def _role_can_advance(user, stage: str) -> bool:
    if user.role == 'super_admin':
        return True
    if user.role == 'admin_staff' and stage in ('hod', 'admin'):
        return True
    if user.role == 'teacher' and stage == 'teacher':
        return True
    return False


class ResultApprovalViewSet(ResultsFeatureMixin, viewsets.ModelViewSet):
    queryset = ResultApproval.objects.select_related('exam__course', 'exam__subject', 'approved_by')
    serializer_class = ResultApprovalSerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    filterset_fields = ['stage', 'exam', 'exam__course', 'exam__term', 'exam__exam_type']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        ids = teacher_course_ids(self.request.user)
        if ids is not None:
            qs = qs.filter(exam__course_id__in=ids)
        return qs

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        approval = self.get_object()
        if approval.exam.is_published:
            return Response({'detail': 'Already published.'}, status=status.HTTP_400_BAD_REQUEST)
        if not _role_can_advance(request.user, approval.stage):
            return Response(
                {'detail': f'Your role cannot approve at stage "{approval.stage}".'},
                status=status.HTTP_403_FORBIDDEN,
            )
        stages = ['teacher', 'hod', 'admin', 'published']
        idx = stages.index(approval.stage) if approval.stage in stages else 0
        if idx < len(stages) - 1:
            approval.stage = stages[idx + 1]
            approval.approved_by = request.user
            approval.save()
            if approval.stage == ResultApproval.Stage.PUBLISHED:
                approval.exam.is_published = True
                approval.exam.save(update_fields=['is_published'])
        return Response(ResultApprovalSerializer(approval).data)


class MarkEntryViewSet(ResultsFeatureMixin, viewsets.ModelViewSet):
    queryset = MarkEntry.objects.select_related(
        'exam__course', 'exam__subject', 'student__user', 'enrollment',
    )
    serializer_class = MarkEntrySerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    filterset_fields = ['exam', 'student', 'exam__course', 'exam__exam_type', 'exam__term']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.STUDENT and hasattr(user, 'student_profile'):
            return qs.filter(
                student=user.student_profile,
                exam__is_published=True,
            )
        ids = teacher_course_ids(user)
        if ids is not None:
            qs = qs.filter(exam__course_id__in=ids)
        course = self.request.query_params.get('course')
        if course:
            qs = qs.filter(exam__course_id=course)
        batch = self.request.query_params.get('batch')
        if batch:
            qs = qs.filter(Q(student__batch_id=batch) | Q(enrollment__batch_id=batch))
        semester = self.request.query_params.get('semester')
        if semester:
            qs = qs.filter(exam__subject__semester=semester)
        return qs.distinct()

    def perform_create(self, serializer):
        entry = serializer.save(entered_by=self.request.user)
        self._apply_grade(entry)

    def perform_update(self, serializer):
        entry = serializer.save(entered_by=self.request.user)
        self._apply_grade(entry)

    def _apply_grade(self, entry):
        policy = GradePolicy.objects.filter(is_active=True).first()
        total = float(entry.internal_marks) + float(entry.external_marks)
        max_marks = float(entry.exam.max_marks) if entry.exam.max_marks else 100
        if entry.exam.subject_id:
            max_marks = float(entry.exam.subject.max_internal + entry.exam.subject.max_external)
        pct = (total / max_marks) * 100 if max_marks else 0
        rules = policy.rules if policy else [
            {'min': 90, 'grade': 'A+'}, {'min': 80, 'grade': 'A'}, {'min': 70, 'grade': 'B'},
            {'min': 60, 'grade': 'C'}, {'min': 50, 'grade': 'D'}, {'min': 0, 'grade': 'F'},
        ]
        entry.grade = calculate_grade(pct, rules)
        if not entry.enrollment_id:
            enr = Enrollment.objects.filter(
                student=entry.student,
                course_id=entry.exam.course_id,
                status=Enrollment.Status.APPROVED,
            ).first()
            if enr:
                entry.enrollment = enr
        entry.save(update_fields=['grade', 'enrollment'])


class MarkSheetView(ResultsFeatureMixin, APIView):
    permission_classes = [IsAuthenticated, CanManageResults]

    @extend_schema(parameters=[MarkSheetQuerySerializer], responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        ser = MarkSheetQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if not user_may_access_course(request.user, data['course']):
            return Response({'detail': 'Not assigned to this program.'}, status=status.HTTP_403_FORBIDDEN)
        payload = build_mark_sheet(
            data['course'], data['semester'], data['exam_type'], data['term'], data.get('batch'),
        )
        return Response(payload)

    @extend_schema(request=MarkSheetSaveSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        ser = MarkSheetSaveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if not user_may_access_course(request.user, data['course']):
            return Response({'detail': 'Not assigned to this program.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role not in ('super_admin', 'admin_staff', 'teacher'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        result = save_mark_sheet(
            data['course'],
            data['semester'],
            data['exam_type'],
            data['term'],
            data.get('entries', []),
            request.user,
            data.get('batch'),
        )
        return Response(result)


ResultAnalysisResponseSerializer = inline_serializer(
    'ResultAnalysisResponse',
    fields={
        'pass_percentage': serializers.FloatField(),
        'top_performers': MarkEntrySerializer(many=True),
    },
)


class ResultAnalysisView(ResultsFeatureMixin, APIView):
    permission_classes = [IsAuthenticated, CanManageResults]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='exam_id', type=int, location=OpenApiParameter.QUERY, required=True),
        ],
        responses={200: ResultAnalysisResponseSerializer},
    )
    def get(self, request):
        exam_id = request.query_params.get('exam_id')
        marks = MarkEntry.objects.filter(exam_id=exam_id)
        total = marks.count()
        passed = marks.exclude(grade='F').count()
        top = marks.order_by('-internal_marks')[:5]
        return Response({
            'pass_percentage': (passed / total * 100) if total else 0,
            'top_performers': MarkEntrySerializer(top, many=True).data,
        })


class MarksheetPDFView(ResultsFeatureMixin, APIView):
    permission_classes = [IsAuthenticated, CanManageResults]

    @extend_schema(responses={(200, 'application/pdf'): OpenApiTypes.BINARY})
    def get(self, request, student_id, exam_id):
        marks = MarkEntry.objects.filter(student_id=student_id, exam_id=exam_id).select_related('exam', 'student__user')
        entry = marks.first()
        if not entry:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        subj = entry.exam.subject.name if entry.exam.subject_id else entry.exam.name
        lines = [f'{subj}: {entry.internal_marks + entry.external_marks} ({entry.grade})']
        gpa = calculate_gpa(marks)
        pdf = generate_marksheet_pdf(entry.student.user.full_name, entry.exam.name, lines, str(gpa))
        return HttpResponse(pdf, content_type='application/pdf')
