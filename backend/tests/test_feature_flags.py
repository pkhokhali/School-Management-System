import pytest
from core.models import InstituteSettings


@pytest.mark.django_db
def test_payments_disabled(auth_client):
    solo = InstituteSettings.get_solo()
    solo.feature_flags['payments_online'] = False
    solo.save()
    response = auth_client.post('/api/v1/fees/online/initiate/', {
        'gateway': 'khalti', 'student_fee_id': 1,
    }, format='json')
    assert response.status_code == 403
