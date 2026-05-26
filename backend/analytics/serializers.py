from rest_framework import serializers


class DashboardAnalyticsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    pending_enrollments = serializers.IntegerField()
    fee_collected = serializers.DecimalField(max_digits=14, decimal_places=2)
    overdue_fees = serializers.IntegerField()
    enrollment_by_status = serializers.ListField(child=serializers.DictField())
    pending_refunds = serializers.IntegerField(required=False)
    installments_due_this_week = serializers.IntegerField(required=False)
    installments_due_amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)


class AttendanceTrendItemSerializer(serializers.Serializer):
    date = serializers.CharField()
    present = serializers.IntegerField()


class AtRiskStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    name = serializers.CharField()
    attendance_pct = serializers.FloatField()
    avg_marks = serializers.FloatField()


class BIReportsSerializer(serializers.Serializer):
    generated_at = serializers.DateTimeField()
    kpis = serializers.DictField()
    enrollment_by_status = serializers.ListField(child=serializers.DictField())
    enrollment_by_course = serializers.ListField(child=serializers.DictField())
    students_by_batch = serializers.ListField(child=serializers.DictField())
    students_by_department = serializers.ListField(child=serializers.DictField())
    course_capacity = serializers.ListField(child=serializers.DictField())
    payments_by_mode = serializers.ListField(child=serializers.DictField())
    fee_collection_by_month = serializers.ListField(child=serializers.DictField())
