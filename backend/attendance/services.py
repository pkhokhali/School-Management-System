import math
from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.utils import timezone

from core.models import InstituteSettings
from courses.models import TeacherAssignment
from events.services import is_institute_holiday
from students.models import Batch, StudentProfile
from students.services import resolve_student_from_qr_payload
from .models import AttendanceRecord, AttendanceSession

PAYROLL_ELIGIBLE_STATUSES = frozenset({
    AttendanceRecord.Status.PRESENT,
    AttendanceRecord.Status.LATE,
})


def validate_geofence(lat, lng):
    settings = InstituteSettings.get_solo()
    geo = settings.campus_geofence or {}
    if geo.get('type') != 'radius':
        return True
    center_lat = geo.get('lat', 0)
    center_lng = geo.get('lng', 0)
    radius_m = geo.get('radius_m', 500)
    dist = _haversine_m(lat, lng, center_lat, center_lng)
    return dist <= radius_m


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def holiday_message(check_date: date, academic_year_id=None):
    if is_institute_holiday(check_date, academic_year_id):
        return 'This date is marked as an institute holiday on the academic calendar.'
    return None


def user_may_mark_on_holiday(user) -> bool:
    role = getattr(user, 'role', None)
    return role in ('super_admin', 'admin_staff')


def get_or_create_register(
    register_date: date,
    batch_id: int,
    course_id: int,
    *,
    period: int = 1,
    teacher=None,
    shift_id=None,
) -> tuple[AttendanceSession, bool]:
    batch = Batch.objects.select_related('shift').get(pk=batch_id)
    if shift_id is None and batch.shift_id:
        shift_id = batch.shift_id
    return AttendanceSession.objects.get_or_create(
        date=register_date,
        batch_id=batch_id,
        course_id=course_id,
        period=period,
        defaults={'teacher': teacher, 'shift_id': shift_id},
    )


def resolve_register(data: dict, user=None) -> tuple[AttendanceSession, list[str]]:
    """Resolve class register from session_id or date+batch+course+period."""
    warnings: list[str] = []
    session = None

    if data.get('session_id'):
        session = AttendanceSession.objects.select_related('batch', 'course', 'shift').get(
            pk=data['session_id']
        )
    else:
        register_date = data.get('date')
        batch_id = data.get('batch')
        course_id = data.get('course')
        if not register_date or not batch_id or not course_id:
            raise ValueError('Provide session_id or date, batch, and course')
        if isinstance(register_date, str):
            register_date = date.fromisoformat(register_date)
        period = int(data.get('period') or 1)
        session, _ = get_or_create_register(
            register_date,
            int(batch_id),
            int(course_id),
            period=period,
            teacher=user if getattr(user, 'role', None) == 'teacher' else None,
            shift_id=data.get('shift'),
        )

    msg = holiday_message(session.date, session.batch.academic_year_id if session.batch else None)
    if msg:
        if user and user_may_mark_on_holiday(user):
            warnings.append(msg)
        else:
            raise ValueError(msg)

    return session, warnings


def resolve_student_for_sync_item(item: dict) -> StudentProfile:
    if item.get('student_id'):
        return StudentProfile.objects.get(pk=item['student_id'])
    if item.get('payload'):
        return resolve_student_from_qr_payload(item['payload'])
    raise ValueError('Each record needs student_id or payload')


def mark_from_qr(session, payload, user, *, gps_lat=None, gps_lng=None, **kwargs):
    if gps_lat is not None and gps_lng is not None and not validate_geofence(float(gps_lat), float(gps_lng)):
        raise ValueError('Outside campus geofence')
    student = resolve_student_from_qr_payload(payload)
    return mark_attendance(
        session, student, kwargs.get('status', AttendanceRecord.Status.PRESENT),
        kwargs.get('source', AttendanceRecord.Source.QR),
        user, kwargs.get('remarks', ''), gps_lat=gps_lat, gps_lng=gps_lng,
    )


def sync_offline_record(item: dict, user) -> dict:
    client_key = str(item.get('client_key', ''))
    try:
        session, warnings = resolve_register(item, user)
        student = resolve_student_for_sync_item(item)
        lat, lng = item.get('gps_lat'), item.get('gps_lng')
        if lat is not None and lng is not None and not validate_geofence(float(lat), float(lng)):
            return {'client_key': client_key, 'ok': False, 'error': 'Outside campus geofence'}

        status = item.get('status', AttendanceRecord.Status.PRESENT)
        if status not in AttendanceRecord.Status.values:
            status = AttendanceRecord.Status.PRESENT

        raw_source = item.get('source', AttendanceRecord.Source.OFFLINE)
        source = (
            AttendanceRecord.Source.OFFLINE
            if raw_source == AttendanceRecord.Source.QR
            else raw_source
            if raw_source in AttendanceRecord.Source.values
            else AttendanceRecord.Source.OFFLINE
        )

        record, created = mark_attendance(
            session, student, status, source, user, item.get('remarks', ''),
            gps_lat=lat, gps_lng=lng,
        )
        result = {
            'client_key': client_key,
            'ok': True,
            'record_id': record.id,
            'session_id': session.id,
            'needs_review': record.needs_review,
            'created': created,
        }
        if warnings:
            result['warnings'] = warnings
        return result
    except ObjectDoesNotExist:
        return {'client_key': client_key, 'ok': False, 'error': 'Register or student not found'}
    except ValueError as exc:
        return {'client_key': client_key, 'ok': False, 'error': str(exc)}
    except Exception as exc:
        return {'client_key': client_key, 'ok': False, 'error': str(exc) or 'Sync failed'}


def mark_attendance(session, student, status, source, user=None, remarks='', gps_lat=None, gps_lng=None):
    existing = AttendanceRecord.objects.filter(session=session, student=student).first()
    needs_review = bool(existing and existing.source != source)
    record, created = AttendanceRecord.objects.update_or_create(
        session=session,
        student=student,
        defaults={
            'status': status,
            'remarks': remarks,
            'source': source,
            'marked_by': user,
            'gps_lat': gps_lat,
            'gps_lng': gps_lng,
            'needs_review': needs_review,
        },
    )
    return record, created


def registers_for_teacher(user, register_date: date | None = None):
    """Teacher's assigned classes for a date, with registers auto-created."""
    register_date = register_date or timezone.localdate()
    assignments = TeacherAssignment.objects.filter(teacher=user).select_related(
        'course', 'batch', 'batch__shift', 'batch__academic_year',
    )
    sessions = []
    for assignment in assignments:
        if not assignment.batch_id:
            continue
        session, _ = get_or_create_register(
            register_date,
            assignment.batch_id,
            assignment.course_id,
            period=1,
            teacher=user,
        )
        sessions.append(session)
    return sessions


def student_attendance_report(from_date: date, to_date: date, batch_id=None, course_id=None):
    qs = AttendanceRecord.objects.filter(
        session__date__gte=from_date,
        session__date__lte=to_date,
    ).select_related('student__user', 'session__course', 'session__batch')
    if batch_id:
        qs = qs.filter(session__batch_id=batch_id)
    if course_id:
        qs = qs.filter(session__course_id=course_id)

    by_student_course = {}
    for record in qs:
        key = (record.student_id, record.session.course_id)
        if key not in by_student_course:
            by_student_course[key] = {
                'student_id': record.student_id,
                'student_name': record.student.user.full_name,
                'enrollment_number': record.student.enrollment_number,
                'course_id': record.session.course_id,
                'course_name': record.session.course.name,
                'batch_name': record.session.batch.name,
                'present': 0,
                'late': 0,
                'absent': 0,
                'total': 0,
            }
        row = by_student_course[key]
        row['total'] += 1
        if record.status == AttendanceRecord.Status.PRESENT:
            row['present'] += 1
        elif record.status == AttendanceRecord.Status.LATE:
            row['late'] += 1
        else:
            row['absent'] += 1

    results = []
    for row in by_student_course.values():
        attended = row['present'] + row['late']
        row['attendance_pct'] = round((attended / row['total']) * 100, 1) if row['total'] else 0
        row['payroll_eligible_days'] = attended
        results.append(row)
    results.sort(key=lambda r: (r['student_name'], r['course_name']))
    return results


def payroll_attendance_summary(from_date: date, to_date: date, batch_id=None, course_id=None):
    """Foundation for payroll: student eligible days + teacher class-days taught."""
    record_qs = AttendanceRecord.objects.filter(
        session__date__gte=from_date,
        session__date__lte=to_date,
    ).select_related('session', 'student__user', 'session__course', 'session__batch', 'session__teacher')
    if batch_id:
        record_qs = record_qs.filter(session__batch_id=batch_id)
    if course_id:
        record_qs = record_qs.filter(session__course_id=course_id)

    students = {}
    for rec in record_qs:
        sid = rec.student_id
        if sid not in students:
            students[sid] = {
                'student_id': sid,
                'student_name': rec.student.user.full_name,
                'enrollment_number': rec.student.enrollment_number,
                'batch_name': rec.session.batch.name,
                'present': 0,
                'late': 0,
                'absent': 0,
                'payroll_eligible': 0,
                'exported': 0,
                'pending_export': 0,
            }
        s = students[sid]
        if rec.status == AttendanceRecord.Status.PRESENT:
            s['present'] += 1
        elif rec.status == AttendanceRecord.Status.LATE:
            s['late'] += 1
        else:
            s['absent'] += 1
        if rec.is_payroll_eligible:
            s['payroll_eligible'] += 1
            if rec.payroll_exported_at:
                s['exported'] += 1
            else:
                s['pending_export'] += 1

    session_qs = AttendanceSession.objects.filter(
        date__gte=from_date,
        date__lte=to_date,
    ).annotate(marked_count=Count('records'))
    if batch_id:
        session_qs = session_qs.filter(batch_id=batch_id)
    if course_id:
        session_qs = session_qs.filter(course_id=course_id)

    teachers = {}
    for session in session_qs.filter(marked_count__gt=0).select_related('teacher', 'course', 'batch'):
        tid = session.teacher_id
        if not tid:
            continue
        if tid not in teachers:
            teachers[tid] = {
                'teacher_id': tid,
                'teacher_name': session.teacher.full_name,
                'class_days': 0,
                'registers': [],
            }
        teachers[tid]['class_days'] += 1
        teachers[tid]['registers'].append({
            'date': session.date.isoformat(),
            'batch': session.batch.name,
            'course': session.course.name,
            'period': session.period,
            'shift': session.shift.name if session.shift_id else None,
            'marked_count': session.marked_count,
        })

    return {
        'from_date': from_date.isoformat(),
        'to_date': to_date.isoformat(),
        'students': sorted(students.values(), key=lambda x: x['student_name']),
        'teachers': sorted(teachers.values(), key=lambda x: x['teacher_name']),
    }


def mark_records_payroll_exported(record_ids: list[int] | None = None, from_date=None, to_date=None):
    qs = AttendanceRecord.objects.filter(
        status__in=PAYROLL_ELIGIBLE_STATUSES,
        payroll_exported_at__isnull=True,
    )
    if record_ids:
        qs = qs.filter(pk__in=record_ids)
    if from_date and to_date:
        qs = qs.filter(session__date__gte=from_date, session__date__lte=to_date)
    now = timezone.now()
    return qs.update(payroll_exported_at=now)
