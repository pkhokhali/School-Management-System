from django.contrib import admin

from .models import AuditLog, DataDeletionRequest, InstituteSettings


@admin.register(InstituteSettings)
class InstituteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not InstituteSettings.objects.exists()


admin.site.register(AuditLog)
admin.site.register(DataDeletionRequest)
