"""Semester / batch billing, scholarships, and late fee application."""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from enrollment.models import Enrollment
from .models import BillingRun, FeeStructure, LateFeePolicy, Scholarship, StudentFeeAssignment
from .services import sync_assignment_status


def _structures_for_enrollment(enrollment, semester=None):
    qs = FeeStructure.objects.filter(course_id=enrollment.course_id)
    if enrollment.batch_id:
        qs = qs.filter(Q(batch_id=enrollment.batch_id) | Q(batch__isnull=True))
    if semester is not None:
        qs = qs.filter(Q(semester=semester) | Q(semester__isnull=True))
    return qs


def _scholarship_discount(structure, scholarship: Scholarship | None, amount: Decimal) -> Decimal:
    if not scholarship:
        return Decimal('0')
    if scholarship.fee_head_id and scholarship.fee_head_id != structure.fee_head_id:
        return Decimal('0')
    return scholarship.calculate_discount(amount)


def _assignment_exists(student_id, structure_id, semester, due_date=None):
    qs = StudentFeeAssignment.objects.filter(student_id=student_id, fee_structure_id=structure_id)
    if semester is not None:
        qs = qs.filter(semester=semester)
    if due_date is not None:
        qs = qs.filter(due_date=due_date)
    return qs.exists()


def run_billing(
    *,
    run_type: str,
    due_date: date,
    course_id=None,
    batch_id=None,
    academic_year_id=None,
    semester=None,
    default_scholarship_id=None,
    apply_scholarship_to_all=True,
    installments=1,
    interval_days=30,
    created_by=None,
    notes='',
) -> BillingRun:
    scholarship = None
    if default_scholarship_id:
        scholarship = Scholarship.objects.filter(pk=default_scholarship_id, is_active=True).first()

    billing_run = BillingRun.objects.create(
        run_type=run_type,
        course_id=course_id,
        batch_id=batch_id,
        academic_year_id=academic_year_id,
        semester=semester,
        due_date=due_date,
        default_scholarship=scholarship,
        notes=notes,
        created_by=created_by,
        status=BillingRun.Status.COMPLETED,
    )

    enrollments = Enrollment.objects.filter(status=Enrollment.Status.APPROVED).select_related(
        'student', 'course', 'batch',
    )
    if course_id:
        enrollments = enrollments.filter(course_id=course_id)
    if batch_id:
        enrollments = enrollments.filter(batch_id=batch_id)
    if semester is not None:
        enrollments = enrollments.filter(
            Q(batch__semester=semester) | Q(student__batch__semester=semester),
        )

    installments = max(int(installments or 1), 1)
    interval_days = max(int(interval_days or 30), 1)
    created = skipped = 0
    for enr in enrollments:
        sem = semester or (enr.batch.semester if enr.batch_id else None)
        for fs in _structures_for_enrollment(enr, semester=sem):
            base = fs.amount
            disc_total = Decimal('0')
            if apply_scholarship_to_all and scholarship:
                disc_total = _scholarship_discount(fs, scholarship, base)

            base_part = (base / installments).quantize(Decimal('0.01'))
            disc_part = (disc_total / installments).quantize(Decimal('0.01')) if disc_total else Decimal('0.00')

            for idx in range(installments):
                installment_due = due_date + timedelta(days=idx * interval_days)
                if _assignment_exists(enr.student_id, fs.id, sem, installment_due):
                    skipped += 1
                    continue

                amount = base_part if idx < installments - 1 else base - (base_part * (installments - 1))
                discount = disc_part if idx < installments - 1 else disc_total - (disc_part * (installments - 1))
                assignment = StudentFeeAssignment.objects.create(
                    student=enr.student,
                    fee_structure=fs,
                    billing_run=billing_run,
                    semester=sem,
                    scholarship=scholarship if discount > 0 else None,
                    total_amount=amount,
                    discount_amount=discount,
                    due_date=installment_due,
                    notes=f'Billing run #{billing_run.id} · installment {idx + 1}/{installments}',
                )
                sync_assignment_status(assignment)
                created += 1

    billing_run.assignments_created = created
    billing_run.assignments_skipped = skipped
    billing_run.save(update_fields=['assignments_created', 'assignments_skipped'])
    return billing_run


def apply_late_fees(policy: LateFeePolicy | None = None) -> dict:
    """Apply active late fee policy to overdue assignments with balance > 0."""
    policy = policy or LateFeePolicy.objects.filter(is_active=True).first()
    if not policy:
        return {'updated': 0, 'detail': 'No active late fee policy'}

    today = date.today()
    cutoff = today - timedelta(days=policy.grace_days)
    updated = 0

    for assignment in StudentFeeAssignment.objects.filter(
        due_date__lt=cutoff,
        status__in=[
            StudentFeeAssignment.PaymentStatus.PENDING,
            StudentFeeAssignment.PaymentStatus.PARTIAL,
            StudentFeeAssignment.PaymentStatus.OVERDUE,
        ],
    ):
        outstanding = assignment.total_amount - assignment.discount_amount - assignment.paid_amount
        if outstanding <= 0:
            continue
        late = (outstanding * policy.rate_percent / Decimal('100')).quantize(Decimal('0.01'))
        if policy.flat_amount > 0:
            late += policy.flat_amount
        if assignment.late_fee != late:
            assignment.late_fee = late
            assignment.save(update_fields=['late_fee', 'updated_at'])
            sync_assignment_status(assignment)
            updated += 1

    return {'updated': updated, 'policy': policy.name}
