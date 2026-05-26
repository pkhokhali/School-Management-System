from django.http import HttpResponse
from django.utils import timezone
from core.services.pdf import generate_enrollment_certificate_pdf
from .models import Enrollment, EnrollmentHistory


def log_status_change(enrollment, new_status, user, note=''):
    EnrollmentHistory.objects.create(
        enrollment=enrollment,
        status=new_status,
        note=note,
        changed_by=user,
    )


def approve_enrollment(enrollment, user):
    enrollment.status = Enrollment.Status.APPROVED
    enrollment.approved_by = user
    enrollment.save()
    log_status_change(enrollment, enrollment.status, user, 'Approved')


def certificate_pdf_response(enrollment):
    pdf = generate_enrollment_certificate_pdf(
        enrollment.student.user.full_name,
        enrollment.course.name,
        timezone.now().strftime('%Y-%m-%d'),
    )
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cert_{enrollment.id}.pdf"'
    return response
