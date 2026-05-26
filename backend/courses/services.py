from django.db import transaction
from django.db.models import Max

from .models import Course


def generate_course_code() -> str:
    """Auto-generate course code: VTS-C000001, VTS-C000002, …"""
    prefix = 'VTS-C'
    with transaction.atomic():
        last = (
            Course.objects.filter(code__startswith=prefix)
            .aggregate(m=Max('code'))
            .get('m')
        )
        if last:
            try:
                seq = int(last.replace(prefix, '')) + 1
            except ValueError:
                seq = Course.objects.count() + 1
        else:
            seq = 1
        return f'{prefix}{seq:06d}'
