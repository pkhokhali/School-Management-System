import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope='session', autouse=True)
def celery_eager():
    from django.conf import settings
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email='testadmin@institute.edu.np',
        password='testpass123',
        first_name='Test', last_name='Admin',
        role=User.Role.SUPER_ADMIN, is_staff=True,
    )
    return user


@pytest.fixture
def auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
