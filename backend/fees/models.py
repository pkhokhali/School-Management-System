from django.conf import settings
from django.db import models


class FeeHead(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)


class LateFeePolicy(models.Model):
    """Institute-wide late fee rule applied by accountant."""

    name = models.CharField(max_length=100)
    grace_days = models.PositiveSmallIntegerField(default=7)
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    flat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Scholarship(models.Model):
    class Type(models.TextChoices):
        PERCENT = 'percent', 'Percentage off'
        FIXED = 'fixed', 'Fixed amount off'

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    scholarship_type = models.CharField(max_length=20, choices=Type.choices, default=Type.PERCENT)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fee_head = models.ForeignKey(
        FeeHead, on_delete=models.SET_NULL, null=True, blank=True, related_name='scholarships',
        help_text='Empty = applies to any fee head',
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def calculate_discount(self, base_amount) -> 'Decimal':
        from decimal import Decimal
        base = Decimal(str(base_amount))
        if self.scholarship_type == self.Type.PERCENT:
            return (base * self.value / Decimal('100')).quantize(Decimal('0.01'))
        return min(self.value, base)


class FeeStructure(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='fee_structures')
    batch = models.ForeignKey('students.Batch', on_delete=models.CASCADE, null=True, blank=True)
    fee_head = models.ForeignKey(FeeHead, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    academic_year = models.ForeignKey('students.AcademicYear', on_delete=models.PROTECT, null=True, blank=True)
    semester = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Bill for specific semester')


class InstallmentPlan(models.Model):
    name = models.CharField(max_length=100)
    installments = models.PositiveSmallIntegerField(default=1)
    interval_days = models.PositiveSmallIntegerField(default=30)


class BillingRun(models.Model):
    """Batch / semester billing execution log (manual or auto)."""

    class RunType(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        SEMESTER = 'semester', 'Semester'
        BATCH = 'batch', 'Batch'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    run_type = models.CharField(max_length=20, choices=RunType.choices, default=RunType.BATCH)
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_runs')
    batch = models.ForeignKey('students.Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_runs')
    academic_year = models.ForeignKey('students.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_runs')
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    due_date = models.DateField()
    default_scholarship = models.ForeignKey(
        Scholarship, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_runs',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    assignments_created = models.PositiveIntegerField(default=0)
    assignments_skipped = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='billing_runs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class StudentFeeAssignment(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = 'paid', 'Paid'
        PARTIAL = 'partial', 'Partial'
        PENDING = 'pending', 'Pending'
        OVERDUE = 'overdue', 'Overdue'

    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='fee_assignments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    billing_run = models.ForeignKey(BillingRun, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Scholarship / waiver')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    late_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['semester', 'student']),
        ]

    @property
    def balance(self):
        return max(
            self.total_amount - self.discount_amount - self.paid_amount + self.late_fee,
            0,
        )


class Payment(models.Model):
    class Mode(models.TextChoices):
        CASH = 'cash', 'Cash'
        CHEQUE = 'cheque', 'Cheque'
        ESEWA = 'esewa', 'eSewa'
        KHALTI = 'khalti', 'Khalti'
        CONNECT_IPS = 'connect_ips', 'Connect IPS'
        FONEPAY = 'fonepay', 'Fonepay'
        ONLINE = 'online', 'Online (other)'

    student_fee = models.ForeignKey(StudentFeeAssignment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mode = models.CharField(max_length=20, choices=Mode.choices)
    receipt_id = models.CharField(max_length=50, unique=True)
    transaction_ref = models.CharField(max_length=200, blank=True)
    gateway_ref = models.CharField(max_length=200, blank=True, help_text='Fonepay / gateway transaction ID')
    is_online = models.BooleanField(default=False)
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RefundRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
