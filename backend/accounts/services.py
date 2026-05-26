import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import OTPVerification
from .tasks import send_otp_email_task


def generate_otp_code():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def create_otp(email='', phone='', purpose=OTPVerification.Purpose.LOGIN):
    code = generate_otp_code()
    expires = timezone.now() + timedelta(minutes=10)
    otp = OTPVerification.objects.create(
        email=email,
        phone=phone,
        code=code,
        purpose=purpose,
        expires_at=expires,
    )
    if email:
        send_otp_email_task.delay(email, code, purpose)
    return otp


def verify_otp(email='', phone='', code='', purpose=OTPVerification.Purpose.LOGIN):
    qs = OTPVerification.objects.filter(
        purpose=purpose,
        is_used=False,
        expires_at__gte=timezone.now(),
        code=code,
    )
    if email:
        qs = qs.filter(email=email)
    if phone:
        qs = qs.filter(phone=phone)
    otp = qs.order_by('-created_at').first()
    if not otp:
        return False
    otp.is_used = True
    otp.save(update_fields=['is_used'])
    return True


def validate_institute_email_domain(email: str) -> bool:
    domain = email.split('@')[-1].lower()
    allowed = [d.lower() for d in settings.INSTITUTE_ALLOWED_EMAIL_DOMAINS]
    return domain in allowed
