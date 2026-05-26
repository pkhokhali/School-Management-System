import pytest
from enrollment.models import Enrollment


@pytest.mark.django_db
def test_enrollment_approve(auth_client, admin_user):
    from django.core.management import call_command
    call_command('seed_demo')
    enrollment = Enrollment.objects.filter(status='approved').first()
    assert enrollment is not None
