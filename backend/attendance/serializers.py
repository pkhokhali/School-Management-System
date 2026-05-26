from rest_framework import serializers

from .models import AttendanceRecord, AttendanceSession


class AttendanceSessionSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    register_label = serializers.SerializerMethodField()
    marked_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'date', 'batch', 'batch_name', 'course', 'course_name',
            'period', 'shift', 'shift_name', 'teacher', 'teacher_name',
            'register_label', 'marked_count', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_register_label(self, obj):
        shift = f' · {obj.shift.name}' if obj.shift_id else ''
        period = f' · P{obj.period}' if obj.period and obj.period > 1 else ''
        return f'{obj.batch.name} · {obj.course.name}{period}{shift}'


class ClassRegisterInputSerializer(serializers.Serializer):
    """Identify or create a class register without exposing internal session IDs."""

    session_id = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)
    batch = serializers.IntegerField(required=False)
    course = serializers.IntegerField(required=False)
    period = serializers.IntegerField(required=False, default=1, min_value=1, max_value=8)
    shift = serializers.IntegerField(required=False, allow_null=True)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    enrollment_number = serializers.CharField(source='student.enrollment_number', read_only=True)
    date = serializers.DateField(source='session.date', read_only=True)
    course_name = serializers.CharField(source='session.course.name', read_only=True)
    batch_name = serializers.CharField(source='session.batch.name', read_only=True)
    period = serializers.IntegerField(source='session.period', read_only=True)
    is_payroll_eligible = serializers.BooleanField(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = '__all__'


class BulkAttendanceSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)
    batch = serializers.IntegerField(required=False)
    course = serializers.IntegerField(required=False)
    period = serializers.IntegerField(required=False, default=1, min_value=1, max_value=8)
    records = serializers.ListField(child=serializers.DictField())


class QRAttendanceSerializer(ClassRegisterInputSerializer):
    payload = serializers.CharField()
    gps_lat = serializers.FloatField(required=False, allow_null=True)
    gps_lng = serializers.FloatField(required=False, allow_null=True)


class OfflineSyncSerializer(serializers.Serializer):
    records = serializers.ListField(child=serializers.DictField())


class OfflineSyncResultSerializer(serializers.Serializer):
    client_key = serializers.CharField(required=False, allow_blank=True)
    ok = serializers.BooleanField(required=False)
    record_id = serializers.IntegerField(required=False)
    session_id = serializers.IntegerField(required=False)
    needs_review = serializers.BooleanField(required=False)
    created = serializers.BooleanField(required=False)
    error = serializers.CharField(required=False, allow_blank=True)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)


class OfflineSyncResponseSerializer(serializers.Serializer):
    synced = OfflineSyncResultSerializer(many=True)
    failed = OfflineSyncResultSerializer(many=True)
    synced_ids = serializers.ListField(child=serializers.IntegerField())


class PayrollExportSerializer(serializers.Serializer):
    record_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
