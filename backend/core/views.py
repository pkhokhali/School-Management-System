from django.conf import settings
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.openapi import DetailResponseSerializer
from .models import AuditLog, DataDeletionRequest, InstituteSettings
from .permissions import IsSuperAdmin
from .serializers import (
    AuditLogSerializer,
    DataDeletionRequestSerializer,
    FeatureFlagsSerializer,
    InstituteSettingsSerializer,
)


FeatureFlagsListResponseSerializer = inline_serializer(
    'FeatureFlagsListResponse',
    fields={'feature_flags': serializers.DictField(child=serializers.BooleanField())},
)


class FeatureListView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: FeatureFlagsListResponseSerializer})
    def get(self, request):
        solo = InstituteSettings.get_solo()
        flags = {**settings.DEFAULT_FEATURE_FLAGS, **(solo.feature_flags or {})}
        return Response({'feature_flags': flags})


class InstituteSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = InstituteSettingsSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_object(self):
        return InstituteSettings.get_solo()


class AdminFeatureFlagsView(views.APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=FeatureFlagsSerializer, responses={200: FeatureFlagsListResponseSerializer})
    def patch(self, request):
        solo = InstituteSettings.get_solo()
        serializer = FeatureFlagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solo.feature_flags = {**solo.feature_flags, **serializer.validated_data['feature_flags']}
        solo.save(update_fields=['feature_flags'])
        return Response({'feature_flags': solo.feature_flags})


class RoleChannelAccessSerializer(serializers.Serializer):
    role_channel_access = serializers.DictField(child=serializers.DictField())


class AdminRoleChannelAccessView(views.APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=RoleChannelAccessSerializer, responses={200: RoleChannelAccessSerializer})
    def patch(self, request):
        solo = InstituteSettings.get_solo()
        serializer = RoleChannelAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solo.role_channel_access = serializer.validated_data['role_channel_access']
        solo.save(update_fields=['role_channel_access'])
        return Response({'role_channel_access': solo.role_channel_access})


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('user').all()[:500]
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class DataDeletionRequestView(generics.ListCreateAPIView):
    serializer_class = DataDeletionRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DataDeletionRequest.objects.none()
        if self.request.user.role == 'super_admin':
            return DataDeletionRequest.objects.all()
        return DataDeletionRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExportCSVView(views.APIView):
    """Generic export placeholder - subclasses override get_data()."""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(responses={(200, 'text/csv'): OpenApiTypes.BINARY})
    def get(self, request):
        import csv
        from io import StringIO
        rows = self.get_export_rows(request)
        buffer = StringIO()
        if rows:
            writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return HttpResponse(buffer.getvalue(), content_type='text/csv')

    def get_export_rows(self, request):
        return []
