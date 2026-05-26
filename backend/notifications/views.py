from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.openapi import DetailResponseSerializer
from .models import DeviceToken, NotificationLog
from .serializers import (
    DeviceTokenSerializer,
    MarkNotificationReadSerializer,
    NotificationLogSerializer,
)


class DeviceTokenView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=DeviceTokenSerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')
        if not token:
            return Response({'detail': 'Token required.'}, status=status.HTTP_400_BAD_REQUEST)
        DeviceToken.objects.update_or_create(
            token=token,
            defaults={'user': request.user, 'platform': platform},
        )
        return Response({'detail': 'Token registered.'})

    @extend_schema(request=DeviceTokenSerializer, responses={204: None})
    def delete(self, request):
        DeviceToken.objects.filter(user=request.user, token=request.data.get('token')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return NotificationLog.objects.none()
        return NotificationLog.objects.filter(user=self.request.user)


class MarkNotificationReadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarkNotificationReadSerializer

    @extend_schema(responses={200: DetailResponseSerializer})
    def post(self, request, pk):
        NotificationLog.objects.filter(user=request.user, pk=pk).update(is_read=True)
        return Response({'detail': 'Marked as read.'})
