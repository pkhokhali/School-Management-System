from django.contrib import admin
from .models import BiometricDevice, BiometricUserMap, WebhookLog
admin.site.register(BiometricDevice)
admin.site.register(BiometricUserMap)
admin.site.register(WebhookLog)
