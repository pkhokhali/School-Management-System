from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LeaveApplicationViewSet, LeaveBalanceViewSet

router = DefaultRouter()
router.register('balances', LeaveBalanceViewSet, basename='leave-balance')
router.register('applications', LeaveApplicationViewSet, basename='leave-app')
urlpatterns = [path('', include(router.urls))]
