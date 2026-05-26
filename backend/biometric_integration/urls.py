from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BiometricDeviceViewSet, BiometricUserMapViewSet, BiometricWebhookView

router = DefaultRouter()
router.register('devices', BiometricDeviceViewSet, basename='biometric-device')
router.register('user-maps', BiometricUserMapViewSet, basename='biometric-map')
urlpatterns = [
    path('webhook/', BiometricWebhookView.as_view(), name='biometric-webhook'),
    path('', include(router.urls)),
]
