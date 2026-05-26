from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import AttendanceRecord
from .reporting import build_bi_report
from .serializers import (
    AtRiskStudentSerializer,
    AttendanceTrendItemSerializer,
    BIReportsSerializer,
    DashboardAnalyticsSerializer,
)
from core.mixins import FeatureFlagViewMixin
from enrollment.models import Enrollment
from fees.models import Payment, RefundRequest, StudentFeeAssignment
from fees.services import sync_assignment_status
from results.models import MarkEntry
from students.models import StudentProfile


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: DashboardAnalyticsSerializer})
    def get(self, request):
        today = timezone.localdate()
        week_end = today + timedelta(days=7)
        pending_refunds = RefundRequest.objects.filter(status=RefundRequest.Status.PENDING).count()
        installments_due_count = 0
        installments_due_amount = 0
        due_qs = StudentFeeAssignment.objects.filter(
            due_date__gte=today,
            due_date__lte=week_end,
        )
        for a in due_qs.iterator():
            sync_assignment_status(a)
            if a.balance > 0:
                installments_due_count += 1
                installments_due_amount += float(a.balance)

        return Response({
            'total_students': StudentProfile.objects.count(),
            'pending_enrollments': Enrollment.objects.filter(status='pending').count(),
            'fee_collected': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_fees': StudentFeeAssignment.objects.filter(status='overdue').count(),
            'enrollment_by_status': list(
                Enrollment.objects.values('status').annotate(count=Count('id'))
            ),
            'pending_refunds': pending_refunds,
            'installments_due_this_week': installments_due_count,
            'installments_due_amount': installments_due_amount,
        })


class BIReportsView(APIView):
    """Management / accountant BI snapshot — students, courses, enrollment, finance."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: BIReportsSerializer})
    def get(self, request):
        return Response(build_bi_report())


class AttendanceTrendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter(name='days', type=int, location=OpenApiParameter.QUERY, required=False)],
        responses={200: AttendanceTrendItemSerializer(many=True)},
    )
    def get(self, request):
        days = int(request.query_params.get('days', 7))
        since = timezone.now().date() - timedelta(days=days)
        data = []
        for i in range(days):
            d = since + timedelta(days=i)
            present = AttendanceRecord.objects.filter(
                session__date=d, status='present',
            ).count()
            data.append({'date': str(d), 'present': present})
        return Response(data)


class AtRiskStudentsView(FeatureFlagViewMixin, APIView):
    feature_key = 'predictive_analytics'
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: AtRiskStudentSerializer(many=True)})
    def get(self, request):
        at_risk = []
        for student in StudentProfile.objects.select_related('user')[:100]:
            total = AttendanceRecord.objects.filter(student=student).count()
            present = AttendanceRecord.objects.filter(
                student=student, status='present',
            ).count()
            att_pct = (present / total * 100) if total else 100
            avg_marks = MarkEntry.objects.filter(student=student).aggregate(
                avg=Sum('internal_marks'),
            )['avg'] or 100
            mark_count = MarkEntry.objects.filter(student=student).count()
            avg = float(avg_marks) / mark_count if mark_count else 100
            if att_pct < 75 and avg < 40:
                at_risk.append({
                    'student_id': student.id,
                    'name': student.user.full_name,
                    'attendance_pct': att_pct,
                    'avg_marks': avg,
                })
        return Response(at_risk)
