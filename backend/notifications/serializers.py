from rest_framework import serializers

from .models import DeviceToken, NotificationLog


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform']
        read_only_fields = ['id']


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = '__all__'
        read_only_fields = ['sent_at']


class MarkNotificationReadSerializer(serializers.Serializer):
    """POST has no body; marks notification as read."""
