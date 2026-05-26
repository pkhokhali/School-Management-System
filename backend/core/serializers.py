from rest_framework import serializers

from .models import AuditLog, DataDeletionRequest, InstituteSettings


class InstituteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteSettings
        fields = [
            'name', 'address', 'phone', 'email', 'logo',
            'feature_flags', 'role_channel_access', 'campus_geofence', 'late_fee_rate_per_day',
        ]
        read_only_fields = ['logo']


class FeatureFlagsSerializer(serializers.Serializer):
    feature_flags = serializers.DictField(child=serializers.BooleanField())


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeletionRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'processed_at']
