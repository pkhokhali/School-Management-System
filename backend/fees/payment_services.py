"""Record counter and gateway (Fonepay) payments on the ledger."""
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model

from .models import Payment, StudentFeeAssignment
from .services import apply_payment_to_assignment

User = get_user_model()


def record_payment(
    *,
    assignment: StudentFeeAssignment,
    amount: Decimal,
    mode: str,
    transaction_ref: str = '',
    gateway_ref: str = '',
    is_online: bool = False,
    cheque_number: str = '',
    notes: str = '',
    recorded_by=None,
) -> Payment:
    receipt_id = f'RCP{uuid.uuid4().hex[:10].upper()}'
    payment = Payment.objects.create(
        student_fee=assignment,
        amount=amount,
        mode=mode,
        receipt_id=receipt_id,
        transaction_ref=transaction_ref,
        gateway_ref=gateway_ref,
        is_online=is_online,
        cheque_number=cheque_number,
        notes=notes,
        recorded_by=recorded_by,
    )
    apply_payment_to_assignment(assignment, amount)
    return payment


def confirm_fonepay_payment(
    *,
    student_fee_id: int,
    amount: Decimal,
    fonepay_txn_id: str,
    recorded_by=None,
) -> Payment:
    """Record a successful Fonepay settlement on the student ledger."""
    assignment = StudentFeeAssignment.objects.select_related('student__user').get(pk=student_fee_id)
    if amount > assignment.balance:
        amount = assignment.balance
    return record_payment(
        assignment=assignment,
        amount=amount,
        mode=Payment.Mode.FONEPAY,
        transaction_ref=fonepay_txn_id,
        gateway_ref=fonepay_txn_id,
        is_online=True,
        notes='Fonepay payment (gateway confirmed)',
        recorded_by=recorded_by,
    )
