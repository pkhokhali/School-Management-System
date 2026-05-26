from django.urls import path

from .views import DeviceTokenView, MarkNotificationReadView, NotificationListView

urlpatterns = [
    path('device-token/', DeviceTokenView.as_view(), name='device-token'),
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification-read'),
]
