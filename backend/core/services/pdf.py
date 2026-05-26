import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from core.models import InstituteSettings


def _institute_header(c, width, height):
    settings = InstituteSettings.get_solo()
    c.setFont('Helvetica-Bold', 16)
    c.drawString(20 * mm, height - 25 * mm, settings.name)
    c.setFont('Helvetica', 10)
    if settings.address:
        c.drawString(20 * mm, height - 32 * mm, settings.address[:80])
    return height - 40 * mm


def generate_simple_pdf(title: str, lines: list[str]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = _institute_header(c, width, height)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(20 * mm, y, title)
    y -= 15 * mm
    c.setFont('Helvetica', 11)
    for line in lines:
        if y < 30 * mm:
            c.showPage()
            y = _institute_header(c, width, height)
        c.drawString(20 * mm, y, line[:100])
        y -= 7 * mm
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_id_card_pdf(student_name: str, enrollment_number: str, batch_name: str) -> bytes:
    lines = [
        f'Student: {student_name}',
        f'Enrollment: {enrollment_number}',
        f'Batch: {batch_name}',
        'Valid for current academic year.',
    ]
    return generate_simple_pdf('Student ID Card', lines)


def generate_receipt_pdf(receipt_id: str, student_name: str, amount: str, mode: str) -> bytes:
    lines = [
        f'Receipt ID: {receipt_id}',
        f'Student: {student_name}',
        f'Amount: NPR {amount}',
        f'Payment Mode: {mode}',
    ]
    return generate_simple_pdf('Payment Receipt', lines)


def generate_marksheet_pdf(student_name: str, exam_name: str, marks_lines: list[str], gpa: str) -> bytes:
    lines = [f'Exam: {exam_name}', f'Student: {student_name}', ''] + marks_lines + ['', f'GPA: {gpa}']
    return generate_simple_pdf('Marksheet', lines)


def generate_enrollment_certificate_pdf(student_name: str, course_name: str, date_str: str) -> bytes:
    lines = [
        f'This certifies that {student_name}',
        f'is enrolled in {course_name}',
        f'as of {date_str}.',
    ]
    return generate_simple_pdf('Enrollment Certificate', lines)
