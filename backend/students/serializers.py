from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AcademicYear, Batch, Department, Shift, StudentDocument, StudentProfile

User = get_user_model()


class ShiftSerializer(serializers.ModelSerializer):
    timing_label = serializers.CharField(read_only=True)

    class Meta:
        model = Shift
        fields = ['id', 'name', 'code', 'start_time', 'end_time', 'is_active', 'timing_label']
        read_only_fields = ['code', 'timing_label']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})
        return attrs


class BatchSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)

    class Meta:
        model = Batch
        fields = '__all__'


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = '__all__'
        read_only_fields = ['student', 'uploaded_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    address = serializers.JSONField(source='user.address', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    documents = StudentDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'email', 'full_name', 'phone', 'address',
            'enrollment_number', 'date_of_birth', 'batch', 'batch_name',
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relation',
            'avatar', 'avatar_url', 'qr_token', 'documents', 'created_at',
        ]
        read_only_fields = ['enrollment_number', 'qr_token', 'created_at', 'avatar']

    def get_avatar_url(self, obj):
        if obj.user.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.avatar.url)
            return obj.user.avatar.url
        return None


class StudentWriteSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'email', 'first_name', 'last_name', 'phone',
            'date_of_birth', 'batch', 'guardian_name', 'guardian_phone',
            'guardian_email', 'guardian_relation',
        ]
        read_only_fields = ['id', 'user']

    def update(self, instance, validated_data):
        user_fields = {}
        for key in ('first_name', 'last_name', 'phone'):
            if key in validated_data:
                user_fields[key] = validated_data.pop(key)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if user_fields:
            for attr, val in user_fields.items():
                setattr(instance.user, attr, val)
            instance.user.save()
        return instance


class StudentRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    address = serializers.JSONField(required=False)
    guardian_name = serializers.CharField(required=False, allow_blank=True)
    guardian_phone = serializers.CharField(required=False, allow_blank=True)
    guardian_email = serializers.EmailField(required=False, allow_blank=True)
    guardian_relation = serializers.CharField(required=False, allow_blank=True)
    batch_id = serializers.IntegerField(required=False, allow_null=True)
