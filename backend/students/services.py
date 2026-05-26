from io import BytesIO

from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse

from .models import StudentProfile


def generate_enrollment_number() -> str:
    """Institute student ID: VTS-S000001, VTS-S000002, …"""
    prefix = 'VTS-S'
    with transaction.atomic():
        last = (
            StudentProfile.objects.filter(enrollment_number__startswith=prefix)
            .aggregate(m=Max('enrollment_number'))
            .get('m')
        )
        if last:
            try:
                seq = int(last.replace(prefix, '')) + 1
            except ValueError:
                seq = StudentProfile.objects.count() + 1
        else:
            seq = 1
        return f'{prefix}{seq:06d}'


def generate_qr_payload(student: StudentProfile) -> str:
    return f'STU:{student.pk}:{student.qr_token[:8]}'


def resolve_student_from_qr_payload(payload: str) -> StudentProfile:
    """Validate student QR string (STU:id:token_prefix) and return the profile."""
    if not payload or not payload.startswith('STU:'):
        raise ValueError('Invalid QR payload')
    parts = payload.split(':')
    if len(parts) < 3:
        raise ValueError('Invalid QR payload')
    try:
        student = StudentProfile.objects.get(pk=parts[1])
    except (StudentProfile.DoesNotExist, ValueError) as exc:
        raise ValueError('Student not found') from exc
    token_prefix = parts[2]
    if not student.qr_token or student.qr_token[:8] != token_prefix:
        raise ValueError('QR token mismatch')
    return student


def generate_qr_image(student: StudentProfile) -> bytes:
    import qrcode
    img = qrcode.make(generate_qr_payload(student))
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def generate_id_card_response(student: StudentProfile) -> HttpResponse:
    from core.services.pdf import generate_id_card_pdf
    batch_name = student.batch.name if student.batch else '—'
    pdf = generate_id_card_pdf(
        student.user.full_name,
        student.enrollment_number,
        batch_name,
    )
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="id_card_{student.enrollment_number}.pdf"'
    return response
