from django.contrib import admin
from .models import DeviceToken, NotificationLog

admin.site.register(DeviceToken)
admin.site.register(NotificationLog)
