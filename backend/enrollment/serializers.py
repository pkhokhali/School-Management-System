from rest_framework import serializers
from .models import Enrollment, EnrollmentHistory


class EnrollmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentHistory
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_enrollment_number = serializers.CharField(source='student.enrollment_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    history = EnrollmentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ['approved_by', 'created_at', 'updated_at']
