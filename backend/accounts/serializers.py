from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import OTPVerification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    role_label = serializers.SerializerMethodField()
    effective_channel_access = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 'full_name',
            'role', 'role_label', 'avatar', 'address', 'is_active',
            'allow_web_portal', 'allow_mobile_app', 'effective_channel_access',
            'must_set_password', 'email_verified', 'created_at',
        ]
        read_only_fields = ['id', 'must_set_password', 'email_verified', 'created_at']

    def get_role_label(self, obj):
        from .role_access import ROLE_LABELS
        return ROLE_LABELS.get(obj.role, obj.role)

    def get_effective_channel_access(self, obj):
        return obj.get_effective_channel_access()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 'phone',
            'role', 'is_active', 'allow_web_portal', 'allow_mobile_app', 'address',
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate_role(self, value):
        request = self.context.get('request')
        if value == User.Role.SUPER_ADMIN and request:
            if request.user.role != User.Role.SUPER_ADMIN:
                raise serializers.ValidationError('Cannot assign Super Admin role.')
        if value == User.Role.SUPER_ADMIN:
            raise serializers.ValidationError('Create super admin via Django admin only.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, email_verified=True, **validated_data)
        if user.role == User.Role.STUDENT:
            from students.models import StudentProfile
            StudentProfile.objects.create(user=user)
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'role', 'is_active',
            'allow_web_portal', 'allow_mobile_app', 'address', 'password',
        ]

    def validate_role(self, value):
        request = self.context.get('request')
        if value == User.Role.SUPER_ADMIN:
            raise serializers.ValidationError('Cannot assign Super Admin role.')
        if self.instance and self.instance.role == User.Role.SUPER_ADMIN:
            if request and request.user != self.instance:
                raise serializers.ValidationError('Cannot modify Super Admin role.')
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            validate_password(password)
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.STUDENT)
    otp_code = serializers.CharField(max_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    client_type = serializers.ChoiceField(choices=['web', 'mobile'], default='web', required=False)


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    purpose = serializers.ChoiceField(choices=OTPVerification.Purpose.choices)


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTPVerification.Purpose.choices)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'address']


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['google', 'microsoft'])
    access_token = serializers.CharField()
    email = serializers.EmailField()


class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class SocialLoginResponseSerializer(AuthTokenResponseSerializer):
    created = serializers.BooleanField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True)


class RolePermissionsResponseSerializer(serializers.Serializer):
    role = serializers.CharField()
    role_label = serializers.CharField()
    permissions = serializers.JSONField()
    assignable_roles = serializers.ListField(child=serializers.CharField())
    all_roles = serializers.DictField(child=serializers.CharField())
    channel_access = serializers.DictField(child=serializers.DictField())
