import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import FeatureFlagViewMixin
from core.services.pdf import generate_receipt_pdf
from core.permissions import IsInstituteAdmin, ReadOnlyOrInstituteAdmin
from .billing_services import apply_late_fees, run_billing
from .gateways import GATEWAYS
from .models import BillingRun, FeeHead, FeeStructure, LateFeePolicy, Payment, RefundRequest, Scholarship, StudentFeeAssignment
from .payment_services import confirm_fonepay_payment, record_payment
from .serializers import (
    BillingRunCreateSerializer,
    BillingRunSerializer,
    BulkAssignFeesSerializer,
    FeeHeadSerializer,
    FeeStructureSerializer,
    FonepayConfirmSerializer,
    LateFeePolicySerializer,
    PaymentSerializer,
    RefundRequestSerializer,
    ScholarshipSerializer,
    StudentFeeAssignmentSerializer,
)
from .services import apply_refund_to_assignment, sync_assignment_status


class FeeHeadViewSet(viewsets.ModelViewSet):
    queryset = FeeHead.objects.all()
    serializer_class = FeeHeadSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]


class LateFeePolicyViewSet(viewsets.ModelViewSet):
    queryset = LateFeePolicy.objects.all()
    serializer_class = LateFeePolicySerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related('fee_head')
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    filterset_fields = ['is_active', 'fee_head']
    search_fields = ['code', 'name']


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('course', 'fee_head', 'batch', 'academic_year')
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    filterset_fields = ['course', 'batch', 'fee_head', 'academic_year', 'semester']


class BillingRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingRun.objects.select_related('course', 'batch', 'default_scholarship', 'created_by')
    serializer_class = BillingRunSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['batch', 'course', 'semester', 'run_type']

    @extend_schema(request=BillingRunCreateSerializer, responses={201: BillingRunSerializer})
    @action(detail=False, methods=['post'], url_path='execute')
    def execute(self, request):
        ser = BillingRunCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        billing_run = run_billing(
            run_type=data['run_type'],
            due_date=data['due_date'],
            course_id=data.get('course'),
            batch_id=data.get('batch'),
            academic_year_id=data.get('academic_year'),
            semester=data.get('semester'),
            default_scholarship_id=data.get('default_scholarship'),
            apply_scholarship_to_all=data.get('apply_scholarship', True),
            installments=data.get('installments', 1),
            interval_days=data.get('interval_days', 30),
            created_by=request.user,
            notes=data.get('notes', ''),
        )
        return Response(BillingRunSerializer(billing_run).data, status=status.HTTP_201_CREATED)


class StudentFeeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = StudentFeeAssignment.objects.select_related(
        'student__user', 'fee_structure__fee_head', 'fee_structure__course', 'scholarship',
    )
    serializer_class = StudentFeeAssignmentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['status', 'student', 'fee_structure__course', 'semester', 'billing_run']
    search_fields = ['student__enrollment_number', 'student__user__first_name', 'student__user__last_name']

    def get_queryset(self):
        qs = super().get_queryset()
        enrollment_number = self.request.query_params.get('enrollment_number')
        if enrollment_number:
            qs = qs.filter(student__enrollment_number__icontains=enrollment_number)
        batch = self.request.query_params.get('batch')
        if batch:
            qs = qs.filter(student__batch_id=batch)
        return qs

    def perform_create(self, serializer):
        assignment = serializer.save()
        sync_assignment_status(assignment)

    def perform_update(self, serializer):
        assignment = serializer.save()
        sync_assignment_status(assignment)

    @extend_schema(request=BulkAssignFeesSerializer, responses={200: inline_serializer(
        'BulkAssignResponse', fields={'created': serializers.IntegerField(), 'skipped': serializers.IntegerField()},
    )})
    @action(detail=False, methods=['post'], url_path='bulk-from-enrollment')
    def bulk_from_enrollment(self, request):
        ser = BulkAssignFeesSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        billing_run = run_billing(
            run_type=BillingRun.RunType.BATCH if data.get('batch') else BillingRun.RunType.MANUAL,
            due_date=data.get('due_date') or date.today(),
            course_id=data.get('course'),
            batch_id=data.get('batch'),
            semester=data.get('semester'),
            created_by=request.user,
        )
        return Response({'created': billing_run.assignments_created, 'skipped': billing_run.assignments_skipped})

    @action(detail=False, methods=['post'], url_path='apply-late-fees')
    def apply_late_fees_action(self, request):
        result = apply_late_fees()
        return Response(result)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'student_fee__student__user', 'student_fee__fee_structure__fee_head',
    )
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['student_fee', 'mode', 'is_online']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        student = self.request.query_params.get('student')
        if student:
            qs = qs.filter(student_fee__student_id=student)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        assignment = data['student_fee']
        is_online = data['mode'] in (
            Payment.Mode.FONEPAY, Payment.Mode.ESEWA, Payment.Mode.KHALTI,
            Payment.Mode.CONNECT_IPS, Payment.Mode.ONLINE,
        )
        payment = record_payment(
            assignment=assignment,
            amount=data['amount'],
            mode=data['mode'],
            transaction_ref=data.get('transaction_ref', ''),
            gateway_ref=data.get('gateway_ref', '') or data.get('transaction_ref', ''),
            is_online=is_online,
            cheque_number=data.get('cheque_number', ''),
            notes=data.get('notes', ''),
            recorded_by=request.user,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='receipt-pdf')
    def receipt_pdf(self, request, pk=None):
        payment = self.get_object()
        label = payment.get_mode_display()
        if payment.gateway_ref:
            label = f'{label} ({payment.gateway_ref})'
        pdf = generate_receipt_pdf(
            payment.receipt_id,
            payment.student_fee.student.user.full_name,
            str(payment.amount),
            label,
        )
        return HttpResponse(pdf, content_type='application/pdf')


class FeeSummaryView(APIView):
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]

    @extend_schema(responses={200: inline_serializer('FeeSummary', fields={
        'collected_today': serializers.DecimalField(max_digits=14, decimal_places=2),
        'collected_month': serializers.DecimalField(max_digits=14, decimal_places=2),
        'outstanding_total': serializers.DecimalField(max_digits=14, decimal_places=2),
        'overdue_count': serializers.IntegerField(),
        'pending_count': serializers.IntegerField(),
        'paid_count': serializers.IntegerField(),
        'fonepay_today': serializers.DecimalField(max_digits=14, decimal_places=2),
        'by_mode_today': serializers.DictField(),
        'pending_refunds': serializers.IntegerField(),
        'installments_due_this_week': serializers.IntegerField(),
        'installments_due_amount': serializers.DecimalField(max_digits=14, decimal_places=2),
    })})
    def get(self, request):
        today = timezone.localdate()
        month_start = today.replace(day=1)
        week_end = today + timedelta(days=7)
        payments_today = Payment.objects.filter(created_at__date=today)
        payments_month = Payment.objects.filter(created_at__date__gte=month_start)

        collected_today = payments_today.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        collected_month = payments_month.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        fonepay_today = payments_today.filter(mode=Payment.Mode.FONEPAY).aggregate(t=Sum('amount'))['t'] or Decimal('0')

        outstanding = overdue_count = pending_count = paid_count = 0
        for a in StudentFeeAssignment.objects.iterator():
            sync_assignment_status(a)
            bal = a.balance
            if bal > 0:
                outstanding += float(bal)
            if a.status == StudentFeeAssignment.PaymentStatus.OVERDUE:
                overdue_count += 1
            elif a.status == StudentFeeAssignment.PaymentStatus.PENDING:
                pending_count += 1
            elif a.status == StudentFeeAssignment.PaymentStatus.PAID:
                paid_count += 1

        by_mode = {}
        for row in payments_today.values('mode').annotate(total=Sum('amount')):
            by_mode[row['mode']] = row['total']

        pending_refunds = RefundRequest.objects.filter(status=RefundRequest.Status.PENDING).count()
        installments_due_count = 0
        installments_due_amount = Decimal('0')
        for a in StudentFeeAssignment.objects.filter(due_date__gte=today, due_date__lte=week_end):
            sync_assignment_status(a)
            if a.balance > 0:
                installments_due_count += 1
                installments_due_amount += a.balance

        return Response({
            'collected_today': collected_today,
            'collected_month': collected_month,
            'outstanding_total': Decimal(str(outstanding)),
            'overdue_count': overdue_count,
            'pending_count': pending_count,
            'paid_count': paid_count,
            'fonepay_today': fonepay_today,
            'by_mode_today': by_mode,
            'pending_refunds': pending_refunds,
            'installments_due_this_week': installments_due_count,
            'installments_due_amount': installments_due_amount,
        })


OnlinePaymentInitSerializer = inline_serializer(
    'OnlinePaymentInit',
    fields={
        'gateway': serializers.CharField(default='fonepay'),
        'student_fee_id': serializers.IntegerField(),
    },
)


class OnlinePaymentInitView(FeatureFlagViewMixin, APIView):
    feature_key = 'payments_online'
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OnlinePaymentInitSerializer, responses={200: inline_serializer(
        'OnlinePaymentInitResponse',
        fields={
            'payment_url': serializers.CharField(required=False),
            'ref': serializers.CharField(),
            'gateway': serializers.CharField(),
        },
    )})
    def post(self, request):
        gateway_name = request.data.get('gateway', 'fonepay')
        fee_id = request.data.get('student_fee_id')
        gateway = GATEWAYS.get(gateway_name)
        if not gateway:
            return Response({'detail': 'Invalid gateway'}, status=status.HTTP_400_BAD_REQUEST)
        fee = StudentFeeAssignment.objects.get(pk=fee_id)
        ref = f'{gateway_name.upper()}-{uuid.uuid4().hex[:8]}'
        result = gateway.initiate(float(fee.balance), ref)
        result['student_fee_id'] = fee_id
        return Response(result)


class FonepayConfirmView(APIView):
    """Mock/production callback to post Fonepay settlement to ledger."""

    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]

    @extend_schema(request=FonepayConfirmSerializer, responses={201: PaymentSerializer})
    def post(self, request):
        ser = FonepayConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payment = confirm_fonepay_payment(
            student_fee_id=ser.validated_data['student_fee_id'],
            amount=ser.validated_data['amount'],
            fonepay_txn_id=ser.validated_data['fonepay_txn_id'],
            recorded_by=request.user,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class RefundRequestViewSet(viewsets.ModelViewSet):
    queryset = RefundRequest.objects.all()
    serializer_class = RefundRequestSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['status', 'payment__student_fee__student']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.role not in ('super_admin', 'admin_staff'):
            return Response({'detail': 'Only accountant/admin can approve refunds.'}, status=status.HTTP_403_FORBIDDEN)
        refund = self.get_object()
        refund.status = RefundRequest.Status.APPROVED
        refund.approved_by = request.user
        refund.save()
        return Response(RefundRequestSerializer(refund).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if request.user.role not in ('super_admin', 'admin_staff'):
            return Response({'detail': 'Only accountant/admin can reject refunds.'}, status=status.HTTP_403_FORBIDDEN)
        refund = self.get_object()
        refund.status = RefundRequest.Status.REJECTED
        refund.approved_by = request.user
        refund.save(update_fields=['status', 'approved_by'])
        return Response(RefundRequestSerializer(refund).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        if request.user.role not in ('super_admin', 'admin_staff'):
            return Response({'detail': 'Only accountant/admin can complete refunds.'}, status=status.HTTP_403_FORBIDDEN)
        refund = self.get_object()
        if refund.status != RefundRequest.Status.APPROVED:
            return Response({'detail': 'Refund must be approved before completion.'}, status=status.HTTP_400_BAD_REQUEST)
        assignment = refund.payment.student_fee
        apply_refund_to_assignment(assignment, refund.amount)
        refund.status = RefundRequest.Status.COMPLETED
        refund.save(update_fields=['status'])
        return Response(RefundRequestSerializer(refund).data)
