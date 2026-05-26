from decimal import Decimal

from django.db import transaction

from courses.models import Course, CourseSubject
from enrollment.models import Enrollment
from .models import Exam, GradePolicy, MarkEntry
from .services import calculate_grade


def _enrollments_for_sheet(course_id, batch_id=None):
    qs = Enrollment.objects.filter(
        course_id=course_id,
        status=Enrollment.Status.APPROVED,
    ).select_related('student__user', 'batch')
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    return qs


def build_mark_sheet(course_id, semester, exam_type, term, batch_id=None):
    course = Course.objects.get(pk=course_id)
    subjects = list(
        CourseSubject.objects.filter(course_id=course_id, semester=semester, is_active=True).order_by('code')
    )
    enrollments = list(_enrollments_for_sheet(course_id, batch_id))

    exams = {}
    for subj in subjects:
        exam, _ = Exam.objects.get_or_create(
            course=course,
            subject=subj,
            exam_type=exam_type,
            term=term,
            defaults={
                'name': f'{subj.name} — {exam_type.replace("_", " ").title()} ({term})',
                'max_marks': subj.max_internal + subj.max_external,
            },
        )
        exams[subj.id] = exam

    exam_ids = [e.id for e in exams.values()]
    marks = MarkEntry.objects.filter(exam_id__in=exam_ids).select_related('exam', 'student__user')
    mark_map = {(m.student_id, m.exam.subject_id): m for m in marks if m.exam.subject_id}

    students = []
    for enr in enrollments:
        sid = enr.student_id
        subject_marks = {}
        for subj in subjects:
            m = mark_map.get((sid, subj.id))
            subject_marks[str(subj.id)] = {
                'mark_id': m.id if m else None,
                'internal_marks': float(m.internal_marks) if m else None,
                'external_marks': float(m.external_marks) if m else None,
                'grade': m.grade if m else '',
                'total': float(m.internal_marks + m.external_marks) if m else None,
            }
        students.append({
            'enrollment_id': enr.id,
            'student_id': sid,
            'student_name': enr.student.user.full_name,
            'enrollment_number': enr.student.enrollment_number,
            'batch_name': enr.batch.name if enr.batch else (enr.student.batch.name if enr.student.batch else ''),
            'marks': subject_marks,
        })

    return {
        'course': {'id': course.id, 'name': course.name, 'code': course.code},
        'semester': semester,
        'exam_type': exam_type,
        'term': term,
        'batch_id': batch_id,
        'subjects': [
            {
                'id': s.id,
                'code': s.code,
                'name': s.name,
                'max_internal': float(s.max_internal),
                'max_external': float(s.max_external),
                'exam_id': exams[s.id].id,
            }
            for s in subjects
        ],
        'students': students,
    }


@transaction.atomic
def save_mark_sheet(course_id, semester, exam_type, term, entries, user, batch_id=None):
    """entries: [{student_id, subject_id, internal_marks, external_marks}]"""
    course = Course.objects.get(pk=course_id)
    subjects = {s.id: s for s in CourseSubject.objects.filter(course_id=course_id, semester=semester, is_active=True)}
    enrollment_by_student = {
        e.student_id: e
        for e in _enrollments_for_sheet(course_id, batch_id)
    }
    policy = GradePolicy.objects.filter(is_active=True).first()
    rules = policy.rules if policy else [
        {'min': 90, 'grade': 'A+'}, {'min': 80, 'grade': 'A'}, {'min': 70, 'grade': 'B'},
        {'min': 60, 'grade': 'C'}, {'min': 50, 'grade': 'D'}, {'min': 0, 'grade': 'F'},
    ]
    saved = 0
    errors = []

    for row in entries:
        student_id = row.get('student_id')
        subject_id = row.get('subject_id')
        if not student_id or not subject_id:
            continue
        subj = subjects.get(int(subject_id))
        if not subj:
            errors.append({'student_id': student_id, 'detail': 'Invalid subject'})
            continue
        enr = enrollment_by_student.get(int(student_id))
        if not enr:
            errors.append({'student_id': student_id, 'detail': 'Student not enrolled in this program'})
            continue

        internal = Decimal(str(row.get('internal_marks') or 0))
        external = Decimal(str(row.get('external_marks') or 0))
        if internal > subj.max_internal:
            errors.append({'student_id': student_id, 'subject_id': subject_id, 'detail': 'Internal marks exceed maximum'})
            continue
        if external > subj.max_external:
            errors.append({'student_id': student_id, 'subject_id': subject_id, 'detail': 'External marks exceed maximum'})
            continue

        exam, _ = Exam.objects.get_or_create(
            course=course,
            subject=subj,
            exam_type=exam_type,
            term=term,
            defaults={
                'name': f'{subj.name} — {exam_type.replace("_", " ").title()} ({term})',
                'max_marks': subj.max_internal + subj.max_external,
            },
        )
        max_marks = exam.max_marks or (subj.max_internal + subj.max_external)
        total = float(internal + external)
        pct = (total / float(max_marks)) * 100 if max_marks else 0
        grade = calculate_grade(pct, rules)

        mark, _ = MarkEntry.objects.update_or_create(
            exam=exam,
            student_id=student_id,
            defaults={
                'enrollment': enr,
                'internal_marks': internal,
                'external_marks': external,
                'grade': grade,
                'entered_by': user,
            },
        )
        saved += 1

    return {'saved': saved, 'errors': errors}
