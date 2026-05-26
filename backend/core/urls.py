from django.urls import path

from .views import (
    AdminFeatureFlagsView,
    AdminRoleChannelAccessView,
    AuditLogListView,
    DataDeletionRequestView,
    FeatureListView,
    InstituteSettingsView,
)

urlpatterns = [
    path('features/', FeatureListView.as_view(), name='features'),
    path('institute/', InstituteSettingsView.as_view(), name='institute-settings'),
    path('admin/features/', AdminFeatureFlagsView.as_view(), name='admin-features'),
    path('admin/role-channel-access/', AdminRoleChannelAccessView.as_view(), name='admin-role-channel-access'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-logs'),
    path('gdpr/deletion-requests/', DataDeletionRequestView.as_view(), name='deletion-requests'),
]
