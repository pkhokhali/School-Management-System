from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_otp_email_task(email, code, purpose):
    try:
        send_mail(
            subject=f'Your OTP for {purpose}',
            message=f'Your verification code is: {code}. Valid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass
