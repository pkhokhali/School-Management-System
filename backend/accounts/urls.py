from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    OTPRequestView,
    OTPVerifyView,
    PasswordResetView,
    ProfileView,
    RegisterView,
    RolePermissionsView,
    SetPasswordView,
    SocialLoginView,
    UserAdminViewSet,
)

router = DefaultRouter()
router.register('users', UserAdminViewSet, basename='admin-user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/set/', SetPasswordView.as_view(), name='set-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('social/', SocialLoginView.as_view(), name='social-login'),
    path('permissions/', RolePermissionsView.as_view(), name='role-permissions'),
    path('', include(router.urls)),
]
