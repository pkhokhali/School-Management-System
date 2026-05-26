import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_register_and_login(api_client):
    api_client.post('/api/v1/auth/otp/request/', {
        'email': 'newuser@institute.edu.np', 'purpose': 'register',
    }, format='json')
    from accounts.models import OTPVerification
    otp = OTPVerification.objects.filter(email='newuser@institute.edu.np').latest('created_at')
    response = api_client.post('/api/v1/auth/register/', {
        'email': 'newuser@institute.edu.np',
        'password': 'SecurePass123!',
        'first_name': 'New', 'last_name': 'User',
        'otp_code': otp.code, 'role': 'student',
    }, format='json')
    assert response.status_code == 201
    login = api_client.post('/api/v1/auth/login/', {
        'email': 'newuser@institute.edu.np', 'password': 'SecurePass123!',
    }, format='json')
    assert login.status_code == 200
    assert 'access' in login.data


@pytest.mark.django_db
def test_features_endpoint(api_client):
    response = api_client.get('/api/v1/features/')
    assert response.status_code == 200
    assert 'feature_flags' in response.data
