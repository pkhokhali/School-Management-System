from datetime import date
from decimal import Decimal

from .models import StudentFeeAssignment


def sync_assignment_status(assignment: StudentFeeAssignment, *, save: bool = True) -> StudentFeeAssignment:
    """Recompute paid status and overdue from amounts and due date."""
    balance = assignment.balance
    if balance <= 0:
        assignment.status = StudentFeeAssignment.PaymentStatus.PAID
    elif assignment.paid_amount > 0:
        assignment.status = StudentFeeAssignment.PaymentStatus.PARTIAL
    else:
        assignment.status = StudentFeeAssignment.PaymentStatus.PENDING

    if balance > 0 and assignment.due_date < date.today():
        assignment.status = StudentFeeAssignment.PaymentStatus.OVERDUE

    if save:
        assignment.save(update_fields=['status'])
    return assignment


def apply_payment_to_assignment(assignment: StudentFeeAssignment, amount: Decimal) -> StudentFeeAssignment:
    assignment.paid_amount = (assignment.paid_amount or Decimal('0')) + amount
    return sync_assignment_status(assignment)


def apply_refund_to_assignment(assignment: StudentFeeAssignment, amount: Decimal) -> StudentFeeAssignment:
    assignment.paid_amount = max((assignment.paid_amount or Decimal('0')) - amount, Decimal('0'))
    return sync_assignment_status(assignment)
