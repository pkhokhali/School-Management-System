import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN_STAFF = 'admin_staff', 'Admin Staff'
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        PARENT = 'parent', 'Parent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    address = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    allow_web_portal = models.BooleanField(
        null=True,
        blank=True,
        help_text='Null = inherit role default; explicit True/False overrides role setting',
    )
    allow_mobile_app = models.BooleanField(
        null=True,
        blank=True,
        help_text='Null = inherit role default; explicit True/False overrides role setting',
    )
    is_staff = models.BooleanField(default=False)
    must_set_password = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        indexes = [models.Index(fields=['role', 'is_active'])]

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_effective_channel_access(self):
        from .role_access import get_channel_access_for_role
        if not self.is_active:
            return {'web_portal': False, 'mobile_app': False}
        role_default = get_channel_access_for_role(self.role)
        return {
            'web_portal': role_default.get('web_portal', False) if self.allow_web_portal is None else self.allow_web_portal,
            'mobile_app': role_default.get('mobile_app', False) if self.allow_mobile_app is None else self.allow_mobile_app,
        }

    def can_use_channel(self, client_type: str) -> bool:
        access = self.get_effective_channel_access()
        if client_type == 'mobile':
            return access['mobile_app']
        return access['web_portal']


class OTPVerification(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'login', 'Login'
        REGISTER = 'register', 'Register'
        RESET_PASSWORD = 'reset_password', 'Reset Password'

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['email', 'phone', 'purpose'])]


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    students = models.ManyToManyField('students.StudentProfile', related_name='guardians', blank=True)
