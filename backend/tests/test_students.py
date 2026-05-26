import pytest
from django.contrib.auth import get_user_model
from students.models import Batch, Department, AcademicYear, StudentProfile

User = get_user_model()


@pytest.mark.django_db
def test_student_register(auth_client):
    dept = Department.objects.create(name='Eng', code='ENG')
    year = AcademicYear.objects.create(name='2025', start_date='2025-01-01', end_date='2025-12-31')
    batch = Batch.objects.create(name='B1', code='B1', department=dept, academic_year=year)
    response = auth_client.post('/api/v1/students/register/', {
        'email': 'sreg@institute.edu.np',
        'password': 'SecurePass123!',
        'first_name': 'Reg', 'last_name': 'Student',
        'batch_id': batch.id,
    }, format='json')
    assert response.status_code == 201
    assert StudentProfile.objects.filter(enrollment_number__startswith='VTS-S').exists()
