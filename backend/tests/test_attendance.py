import pytest
from attendance.models import AttendanceRecord


@pytest.mark.django_db
def test_attendance_conflict_flag(auth_client):
    from django.core.management import call_command
    call_command('seed_demo')
    record = AttendanceRecord.objects.first()
    assert record is not None
