from .models import AuditLog


class AuditLogMiddleware:
    MUTATING_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capture request payload for auditing (best-effort; avoid large/binary bodies).
        request._audit_payload = {}
        try:
            if request.content_type and 'application/json' in request.content_type:
                request._audit_payload = getattr(request, 'data', {}) or {}
        except Exception:
            request._audit_payload = {}

        response = self.get_response(request)
        if (
            request.method in self.MUTATING_METHODS
            and request.path.startswith('/api/')
            and getattr(request, 'user', None)
            and request.user.is_authenticated
        ):
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                model_name=request.path,
                object_id=str(getattr(getattr(request, 'resolver_match', None), 'kwargs', {}).get('pk', '') or ''),
                changes={'payload': request._audit_payload} if request._audit_payload else {},
                ip_address=self._get_client_ip(request),
            )
        return response

    @staticmethod
    def _get_client_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
