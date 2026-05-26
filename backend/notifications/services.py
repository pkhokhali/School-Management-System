import logging

from .models import DeviceToken, NotificationLog

logger = logging.getLogger(__name__)


def send_push_to_user(user, title: str, body: str, data: dict = None):
    """Send FCM push - logs if firebase not configured."""
    NotificationLog.objects.create(user=user, title=title, body=body, data=data or {})
    tokens = list(DeviceToken.objects.filter(user=user).values_list('token', flat=True))
    if not tokens:
        return False
    try:
        import firebase_admin
        from firebase_admin import messaging
        if not firebase_admin._apps:
            logger.info('FCM not initialized - notification logged only')
            return False
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            tokens=tokens,
        )
        messaging.send_each_for_multicast(message)
        return True
    except Exception as e:
        logger.warning('FCM send failed: %s', e)
        return False
