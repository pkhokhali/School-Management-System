"""Seed rich fee / billing / Fonepay demo data. Run: python manage.py seed_fee_demo"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from courses.models import Course
from enrollment.models import Enrollment
from fees.billing_services import apply_late_fees, run_billing
from fees.models import FeeHead, FeeStructure, LateFeePolicy, Payment, RefundRequest, Scholarship, StudentFeeAssignment
from fees.payment_services import confirm_fonepay_payment, record_payment
from students.models import AcademicYear, Batch, StudentProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed fee billing, scholarships, late fees, and Fonepay payments for testing'

    def handle(self, *args, **options):
        super_admin = User.objects.filter(email='admin@institute.edu.np').first()
        year = AcademicYear.objects.filter(is_current=True).first()
        batch = Batch.objects.first()
        course = Course.objects.first()
        if not all([year, batch, course]):
            self.stdout.write(self.style.ERROR('Run seed_demo first (year, batch, course).'))
            return

        LateFeePolicy.objects.get_or_create(
            name='Standard late fee',
            defaults={'grace_days': 7, 'rate_percent': Decimal('2'), 'flat_amount': Decimal('500'), 'is_active': True},
        )

        heads = {}
        for code, name, amount in [
            ('TUITION', 'Tuition Fee', 50000),
            ('EXAM', 'Exam Fee', 3500),
            ('LAB', 'Lab Fee', 8000),
        ]:
            h, _ = FeeHead.objects.get_or_create(code=code, defaults={'name': name})
            heads[code] = h
            FeeStructure.objects.get_or_create(
                course=course, batch=batch, fee_head=h, semester=1,
                defaults={'amount': amount, 'academic_year': year},
            )
            FeeStructure.objects.get_or_create(
                course=course, batch=batch, fee_head=h, semester=2,
                defaults={'amount': amount * Decimal('0.5'), 'academic_year': year},
            )

        merit, _ = Scholarship.objects.get_or_create(
            code='MERIT-25',
            defaults={
                'name': 'Merit scholarship 25%',
                'scholarship_type': Scholarship.Type.PERCENT,
                'value': Decimal('25'),
            },
        )
        Scholarship.objects.get_or_create(
            code='STAFF-WARD',
            defaults={
                'name': 'Staff ward fixed NPR 10000',
                'scholarship_type': Scholarship.Type.FIXED,
                'value': Decimal('10000'),
                'fee_head': heads['TUITION'],
            },
        )

        billing = run_billing(
            run_type='semester',
            due_date=date.today() + timedelta(days=15),
            course_id=course.id,
            batch_id=batch.id,
            semester=1,
            default_scholarship_id=merit.id,
            apply_scholarship_to_all=False,
            installments=2,
            interval_days=30,
            created_by=super_admin,
            notes='Demo semester 1 billing',
        )

        overdue = StudentFeeAssignment.objects.filter(student__batch=batch).first()
        if overdue:
            overdue.due_date = date.today() - timedelta(days=20)
            overdue.paid_amount = Decimal('10000')
            overdue.discount_amount = Decimal('5000')
            overdue.save()
            apply_late_fees()

        profiles = list(StudentProfile.objects.filter(batch=batch)[:6])
        if len(profiles) >= 2:
            a1 = StudentFeeAssignment.objects.filter(student=profiles[0]).first()
            if a1:
                record_payment(
                    assignment=a1,
                    amount=Decimal('15000'),
                    mode=Payment.Mode.CASH,
                    recorded_by=super_admin,
                )
            a2 = StudentFeeAssignment.objects.filter(student=profiles[1]).first()
            if a2 and a2.balance > 0:
                confirm_fonepay_payment(
                    student_fee_id=a2.id,
                    amount=min(a2.balance, Decimal('20000')),
                    fonepay_txn_id='FPY-DEMO-20260525-001',
                    recorded_by=super_admin,
                )
            a3 = StudentFeeAssignment.objects.filter(student=profiles[2]).first() if len(profiles) > 2 else None
            if a3 and a3.balance > 0:
                confirm_fonepay_payment(
                    student_fee_id=a3.id,
                    amount=min(a3.balance, Decimal('10000')),
                    fonepay_txn_id='FPY-DEMO-20260525-002',
                    recorded_by=super_admin,
                )
            a4 = StudentFeeAssignment.objects.filter(student=profiles[3]).first() if len(profiles) > 3 else None
            if a4:
                p4 = Payment.objects.filter(student_fee=a4).first()
                if p4:
                    RefundRequest.objects.get_or_create(
                        payment=p4,
                        amount=min(Decimal('2000'), p4.amount),
                        reason='Demo partial refund (withdrawn lab component)',
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Fee demo seeded: billing run #{billing.id}, '
            f'{Payment.objects.filter(mode=Payment.Mode.FONEPAY).count()} Fonepay payments, '
            f'installments and refund workflow demo ready.',
        ))
