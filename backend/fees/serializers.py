from rest_framework import serializers

from .models import (
    BillingRun,
    FeeHead,
    FeeStructure,
    InstallmentPlan,
    LateFeePolicy,
    Payment,
    RefundRequest,
    Scholarship,
    StudentFeeAssignment,
)


class FeeHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeHead
        fields = '__all__'


class LateFeePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LateFeePolicy
        fields = '__all__'


class ScholarshipSerializer(serializers.ModelSerializer):
    fee_head_name = serializers.CharField(source='fee_head.name', read_only=True, allow_null=True)

    class Meta:
        model = Scholarship
        fields = [
            'id', 'code', 'name', 'scholarship_type', 'value', 'fee_head', 'fee_head_name',
            'is_active', 'notes',
        ]


class FeeStructureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    fee_head_name = serializers.CharField(source='fee_head.name', read_only=True)
    fee_head_code = serializers.CharField(source='fee_head.code', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True, allow_null=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True, allow_null=True)

    class Meta:
        model = FeeStructure
        fields = [
            'id', 'course', 'course_name', 'course_code', 'batch', 'batch_name',
            'fee_head', 'fee_head_name', 'fee_head_code', 'amount', 'academic_year',
            'academic_year_name', 'semester',
        ]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = '__all__'


class BillingRunSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True, allow_null=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True, allow_null=True)
    scholarship_name = serializers.CharField(source='default_scholarship.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = BillingRun
        fields = [
            'id', 'run_type', 'course', 'course_name', 'batch', 'batch_name', 'academic_year',
            'semester', 'due_date', 'default_scholarship', 'scholarship_name', 'status',
            'assignments_created', 'assignments_skipped', 'notes', 'created_by', 'created_by_name',
            'created_at',
        ]
        read_only_fields = ['assignments_created', 'assignments_skipped', 'created_at', 'created_by']


class StudentFeeAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    enrollment_number = serializers.CharField(source='student.enrollment_number', read_only=True)
    fee_head_name = serializers.CharField(source='fee_structure.fee_head.name', read_only=True)
    course_name = serializers.CharField(source='fee_structure.course.name', read_only=True)
    scholarship_name = serializers.CharField(source='scholarship.name', read_only=True, allow_null=True)
    balance = serializers.SerializerMethodField()
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = StudentFeeAssignment
        fields = [
            'id', 'student', 'student_name', 'enrollment_number', 'fee_structure',
            'fee_head_name', 'course_name', 'billing_run', 'semester', 'scholarship', 'scholarship_name',
            'total_amount', 'discount_amount', 'net_amount', 'paid_amount', 'balance', 'late_fee',
            'due_date', 'status', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['paid_amount', 'status', 'created_at', 'updated_at']

    def get_net_amount(self, obj):
        return obj.total_amount - obj.discount_amount

    def get_balance(self, obj):
        return obj.balance


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student_fee.student.user.full_name', read_only=True)
    enrollment_number = serializers.CharField(source='student_fee.student.enrollment_number', read_only=True)
    fee_head_name = serializers.CharField(source='student_fee.fee_structure.fee_head.name', read_only=True)
    mode_label = serializers.CharField(source='get_mode_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student_fee', 'student_name', 'enrollment_number', 'fee_head_name',
            'amount', 'mode', 'mode_label', 'receipt_id', 'transaction_ref', 'gateway_ref',
            'is_online', 'cheque_number', 'notes', 'recorded_by', 'created_at',
        ]
        read_only_fields = ['receipt_id', 'recorded_by', 'created_at']


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = '__all__'


class BulkAssignFeesSerializer(serializers.Serializer):
    course = serializers.IntegerField(required=False, allow_null=True)
    batch = serializers.IntegerField(required=False, allow_null=True)
    semester = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)


class BillingRunCreateSerializer(serializers.Serializer):
    run_type = serializers.ChoiceField(choices=BillingRun.RunType.choices, default='batch')
    course = serializers.IntegerField(required=False, allow_null=True)
    batch = serializers.IntegerField(required=False, allow_null=True)
    academic_year = serializers.IntegerField(required=False, allow_null=True)
    semester = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField()
    default_scholarship = serializers.IntegerField(required=False, allow_null=True)
    apply_scholarship = serializers.BooleanField(default=True)
    installments = serializers.IntegerField(required=False, min_value=1, default=1)
    interval_days = serializers.IntegerField(required=False, min_value=1, default=30)
    notes = serializers.CharField(required=False, allow_blank=True)


class FonepayConfirmSerializer(serializers.Serializer):
    student_fee_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    fonepay_txn_id = serializers.CharField(max_length=200)
