"""Institute BI / management reporting aggregates."""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from accounts.models import User
from announcements.models import Announcement
from attendance.models import AttendanceRecord
from courses.models import Course
from enrollment.models import Enrollment
from fees.models import Payment, RefundRequest, StudentFeeAssignment
from fees.services import sync_assignment_status
from students.models import Batch, Department, StudentProfile


def _sum_balance(assignments):
    total = Decimal('0')
    for a in assignments:
        sync_assignment_status(a)
        if a.balance > 0:
            total += a.balance
    return total


def build_bi_report() -> dict:
    today = timezone.localdate()
    month_start = today.replace(day=1)
    week_end = today + timedelta(days=7)

    students_qs = StudentProfile.objects.select_related('batch', 'batch__department')
    total_students = students_qs.count()
    students_with_batch = students_qs.filter(batch__isnull=False).count()

    courses_qs = Course.objects.all()
    total_courses = courses_qs.count()
    active_courses = courses_qs.filter(is_active=True).count()

    enrollments = Enrollment.objects.select_related('course', 'student')
    enrollment_by_status = list(
        enrollments.values('status').annotate(count=Count('id')).order_by('status'),
    )
    approved_enrollments = enrollments.filter(status=Enrollment.Status.APPROVED).count()

    enrollment_by_course = list(
        enrollments.filter(status=Enrollment.Status.APPROVED)
        .values('course__code', 'course__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:15],
    )
    enrollment_by_course = [
        {
            'course_code': row['course__code'] or '—',
            'course_name': row['course__name'] or '—',
            'count': row['count'],
        }
        for row in enrollment_by_course
    ]

    students_by_batch = list(
        students_qs.filter(batch__isnull=False)
        .values('batch__name', 'batch__code')
        .annotate(count=Count('id'))
        .order_by('-count')[:12],
    )
    students_by_batch = [
        {'batch_name': r['batch__name'], 'batch_code': r['batch__code'], 'count': r['count']}
        for r in students_by_batch
    ]

    students_by_department = list(
        students_qs.filter(batch__department__isnull=False)
        .values('batch__department__name', 'batch__department__code')
        .annotate(count=Count('id'))
        .order_by('-count'),
    )
    students_by_department = [
        {
            'department_name': r['batch__department__name'],
            'department_code': r['batch__department__code'],
            'count': r['count'],
        }
        for r in students_by_department
    ]

    course_capacity = []
    for course in courses_qs.filter(is_active=True)[:20]:
        enrolled = enrollments.filter(course=course, status=Enrollment.Status.APPROVED).count()
        cap = course.max_enrollment or 0
        util = round(enrolled / cap * 100, 1) if cap else 0
        course_capacity.append({
            'course_code': course.code,
            'course_name': course.name,
            'enrolled': enrolled,
            'capacity': cap,
            'utilization_pct': util,
        })
    course_capacity.sort(key=lambda x: x['utilization_pct'], reverse=True)

    payments_month = (
        Payment.objects.filter(created_at__date__gte=month_start)
        .aggregate(total=Sum('amount'))['total'] or Decimal('0')
    )
    fee_collected_all = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    outstanding = Decimal('0')
    overdue_count_n = 0
    for a in StudentFeeAssignment.objects.iterator():
        sync_assignment_status(a)
        if a.balance > 0:
            outstanding += a.balance
        if a.status == StudentFeeAssignment.PaymentStatus.OVERDUE:
            overdue_count_n += 1

    payments_by_mode = list(
        Payment.objects.values('mode')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total'),
    )
    payments_by_mode = [
        {'mode': r['mode'], 'total': r['total'] or 0, 'count': r['count']}
        for r in payments_by_mode
    ]

    six_months_ago = today.replace(day=1) - timedelta(days=180)
    fee_by_month = []
    monthly = (
        Payment.objects.filter(created_at__date__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    for row in monthly:
        fee_by_month.append({
            'month': row['month'].strftime('%Y-%m') if row['month'] else '',
            'amount': row['total'] or 0,
        })

    att_total = AttendanceRecord.objects.count()
    att_present = AttendanceRecord.objects.filter(status='present').count()
    att_rate = round(att_present / att_total * 100, 1) if att_total else 0

    pending_refunds = RefundRequest.objects.filter(status=RefundRequest.Status.PENDING).count()
    installments_due = StudentFeeAssignment.objects.filter(
        due_date__gte=today,
        due_date__lte=week_end,
        status__in=[
            StudentFeeAssignment.PaymentStatus.PENDING,
            StudentFeeAssignment.PaymentStatus.PARTIAL,
            StudentFeeAssignment.PaymentStatus.OVERDUE,
        ],
    )
    installments_due_count = 0
    installments_due_amount = Decimal('0')
    for a in installments_due.iterator():
        sync_assignment_status(a)
        if a.balance > 0:
            installments_due_count += 1
            installments_due_amount += a.balance

    return {
        'generated_at': timezone.now().isoformat(),
        'kpis': {
            'total_students': total_students,
            'students_with_batch': students_with_batch,
            'total_courses': total_courses,
            'active_courses': active_courses,
            'total_batches': Batch.objects.count(),
            'total_departments': Department.objects.count(),
            'total_enrollments': enrollments.count(),
            'approved_enrollments': approved_enrollments,
            'pending_enrollments': enrollments.filter(status=Enrollment.Status.PENDING).count(),
            'dropped_enrollments': enrollments.filter(status=Enrollment.Status.DROPPED).count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'admin_staff': User.objects.filter(role='admin_staff').count(),
            'fee_collected_all_time': fee_collected_all,
            'fee_collected_month': payments_month,
            'outstanding_fees': outstanding,
            'overdue_accounts': overdue_count_n,
            'attendance_records': att_total,
            'attendance_present_rate': att_rate,
            'published_announcements': Announcement.objects.filter(
                status=Announcement.Status.PUBLISHED,
            ).count(),
            'pending_refunds': pending_refunds,
            'installments_due_this_week': installments_due_count,
            'installments_due_amount': installments_due_amount,
        },
        'enrollment_by_status': enrollment_by_status,
        'enrollment_by_course': enrollment_by_course,
        'students_by_batch': students_by_batch,
        'students_by_department': students_by_department,
        'course_capacity': course_capacity,
        'payments_by_mode': payments_by_mode,
        'fee_collection_by_month': fee_by_month,
    }
