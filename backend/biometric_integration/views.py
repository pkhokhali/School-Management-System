import hashlib
import hmac
from datetime import date

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import AttendanceRecord
from attendance.services import get_or_create_register, mark_attendance
from core.openapi import DetailResponseSerializer
from students.models import StudentProfile
from .models import BiometricDevice, BiometricUserMap, WebhookLog
from rest_framework import serializers

BiometricWebhookSerializer = inline_serializer(
    'BiometricWebhook',
    fields={
        'device_id': serializers.CharField(),
        'user_id': serializers.CharField(),
        'status': serializers.CharField(required=False),
        'course_id': serializers.IntegerField(required=False),
        'period': serializers.IntegerField(required=False),
    },
)


class BiometricDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricDevice
        fields = '__all__'


class BiometricUserMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricUserMap
        fields = '__all__'


class BiometricDeviceViewSet(viewsets.ModelViewSet):
    queryset = BiometricDevice.objects.all()
    serializer_class = BiometricDeviceSerializer
    permission_classes = [IsAuthenticated]


class BiometricUserMapViewSet(viewsets.ModelViewSet):
    queryset = BiometricUserMap.objects.select_related('device', 'user', 'student')
    serializer_class = BiometricUserMapSerializer
    permission_classes = [IsAuthenticated]


class BiometricWebhookView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=BiometricWebhookSerializer,
        responses={200: DetailResponseSerializer, 401: DetailResponseSerializer, 404: DetailResponseSerializer},
    )
    def post(self, request):
        signature = request.headers.get('X-Signature', '')
        body = request.body
        expected = hmac.new(
            settings.BIOMETRIC_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return Response({'detail': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        WebhookLog.objects.create(device_id=data.get('device_id', ''), payload=data)

        user_id = data.get('user_id')
        device_id = data.get('device_id')
        status_val = data.get('status', 'present')
        try:
            device = BiometricDevice.objects.get(device_id=device_id)
            mapping = BiometricUserMap.objects.get(device=device, device_user_id=user_id)
        except Exception:
            return Response({'detail': 'Mapping not found'}, status=status.HTTP_404_NOT_FOUND)

        student = mapping.student
        if not student or not student.batch_id:
            return Response({'detail': 'No student linked or student has no batch'}, status=status.HTTP_400_BAD_REQUEST)

        course_id = data.get('course_id') or (device.default_course_id if device.default_course_id else None)
        if not course_id:
            return Response(
                {'detail': 'course_id required in webhook or set default_course on device'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        period = int(data.get('period') or device.default_period or 1)
        today = date.today()
        try:
            session, _ = get_or_create_register(
                today, student.batch_id, int(course_id), period=period,
            )
        except Exception:
            return Response({'detail': 'Could not open class register'}, status=status.HTTP_400_BAD_REQUEST)

        att_status = AttendanceRecord.Status.PRESENT if status_val == 'present' else AttendanceRecord.Status.ABSENT
        mark_attendance(session, student, att_status, AttendanceRecord.Source.BIOMETRIC)
        return Response({'detail': 'Processed', 'session_id': session.id})
