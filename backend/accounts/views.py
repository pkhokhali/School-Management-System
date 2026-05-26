from django.contrib.auth import get_user_model
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from core.openapi import DetailResponseSerializer
from core.permissions import IsSuperAdmin
from .models import OTPVerification
from .role_access import ASSIGNABLE_ROLES, MODULE_ACCESS, ROLE_LABELS, get_permissions_for_role
from .serializers import (
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    LoginSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    PasswordResetSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    SetPasswordSerializer,
    SocialLoginSerializer,
    SocialLoginResponseSerializer,
    AuthTokenResponseSerializer,
    LogoutSerializer,
    RolePermissionsResponseSerializer,
    UserSerializer,
)
from .services import create_otp, validate_institute_email_domain, verify_otp

User = get_user_model()


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: AuthTokenResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not verify_otp(email=data['email'], code=data['otp_code'], purpose=OTPVerification.Purpose.REGISTER):
            return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            phone=data.get('phone', ''),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            email_verified=True,
        )
        tokens = get_tokens_for_user(user)
        return Response({**tokens, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(request=LoginSerializer, responses={200: AuthTokenResponseSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        client_type = serializer.validated_data.get('client_type', 'web')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': 'Account disabled.'}, status=status.HTTP_403_FORBIDDEN)
        if not user.can_use_channel(client_type):
            label = 'mobile app' if client_type == 'mobile' else 'web portal'
            return Response(
                {'detail': f'Access denied for {label}.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data
        user_data['permissions'] = get_permissions_for_role(user.role)
        return Response({**tokens, 'user': user_data})


class OTPRequestView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(request=OTPRequestSerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not data.get('email') and not data.get('phone'):
            return Response({'detail': 'Email or phone required.'}, status=status.HTTP_400_BAD_REQUEST)
        create_otp(email=data.get('email', ''), phone=data.get('phone', ''), purpose=data['purpose'])
        return Response({'detail': 'OTP sent.'})


class OTPVerifyView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=OTPVerifySerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ok = verify_otp(
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            code=data['code'],
            purpose=data['purpose'],
        )
        if not ok:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'OTP verified.'})


class PasswordResetView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetSerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not verify_otp(email=data['email'], code=data['otp_code'], purpose=OTPVerification.Purpose.RESET_PASSWORD):
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(data['new_password'])
        user.must_set_password = False
        user.save()
        return Response({'detail': 'Password reset successful.'})


class SetPasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=SetPasswordSerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.must_set_password = False
        request.user.save()
        return Response({'detail': 'Password updated.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class SocialLoginView(views.APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=SocialLoginSerializer, responses={200: SocialLoginResponseSerializer})
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if not validate_institute_email_domain(email):
            return Response(
                {'detail': f'Email must use domain: {settings.INSTITUTE_ALLOWED_EMAIL_DOMAINS}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': email.split('@')[0],
                'last_name': '',
                'role': User.Role.STUDENT,
                'email_verified': True,
            },
        )
        if created:
            user.set_unusable_password()
            user.must_set_password = True
            user.save()
        tokens = get_tokens_for_user(user)
        return Response({**tokens, 'user': UserSerializer(user).data, 'created': created})


class RolePermissionsView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: RolePermissionsResponseSerializer})
    def get(self, request):
        role = request.user.role
        return Response({
            'role': role,
            'role_label': ROLE_LABELS.get(role, role),
            'permissions': get_permissions_for_role(role),
            'assignable_roles': ASSIGNABLE_ROLES if role == 'super_admin' else [],
            'all_roles': ROLE_LABELS,
        })


class UserAdminViewSet(viewsets.ModelViewSet):
    """Super admin: create reception, teachers, students with role-based access."""
    queryset = User.objects.exclude(role=User.Role.SUPER_ADMIN).order_by('-created_at')
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AdminUserUpdateSerializer
        return UserSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(detail=False, methods=['get'])
    def role_options(self, request):
        from core.models import InstituteSettings
        solo = InstituteSettings.get_solo()
        return Response({
            'roles': ASSIGNABLE_ROLES,
            'access_matrix': MODULE_ACCESS,
            'channel_access': solo.role_channel_access,
        })


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={200: DetailResponseSerializer})
    def post(self, request):
        try:
            refresh = request.data.get('refresh')
            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out.'})


class CustomTokenRefreshView(TokenRefreshView):
    pass
