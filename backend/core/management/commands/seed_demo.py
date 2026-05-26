from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import InstituteSettings
from students.models import Department, AcademicYear, Batch, Shift, StudentProfile
from courses.models import Course, CourseSubject, TeacherAssignment
from enrollment.models import Enrollment
from announcements.models import Announcement
from attendance.models import AttendanceSession, AttendanceRecord
from events.models import CalendarEvent
from fees.models import FeeHead, FeeStructure, StudentFeeAssignment
from results.models import Exam, GradePolicy, MarkEntry, ResultApproval

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for testing'

    def handle(self, *args, **options):
        InstituteSettings.get_solo()
        self.stdout.write('Seeding institute settings...')

        dept, _ = Department.objects.get_or_create(code='CS', defaults={'name': 'Computer Science'})
        year, _ = AcademicYear.objects.get_or_create(
            name='2025-2026',
            defaults={'start_date': date(2025, 1, 1), 'end_date': date(2026, 12, 31), 'is_current': True},
        )
        from datetime import time
        morning, _ = Shift.objects.get_or_create(
            code='MORNING',
            defaults={
                'name': 'Morning',
                'start_time': time(7, 0),
                'end_time': time(12, 0),
                'is_active': True,
            },
        )
        Shift.objects.get_or_create(
            code='EVENING',
            defaults={
                'name': 'Evening',
                'start_time': time(14, 0),
                'end_time': time(18, 0),
                'is_active': True,
            },
        )
        batch, _ = Batch.objects.get_or_create(
            code='CS-2025-A',
            defaults={
                'name': 'CS Year 1 A', 'department': dept, 'academic_year': year,
                'semester': 1, 'shift': morning,
            },
        )

        super_admin, _ = User.objects.get_or_create(
            email='admin@institute.edu.np',
            defaults={
                'first_name': 'Super', 'last_name': 'Admin',
                'role': User.Role.SUPER_ADMIN, 'is_staff': True, 'is_superuser': True,
            },
        )
        if _:
            super_admin.set_password('admin123')
            super_admin.save()

        teacher, _ = User.objects.get_or_create(
            email='teacher@institute.edu.np',
            defaults={'first_name': 'John', 'last_name': 'Teacher', 'role': User.Role.TEACHER},
        )
        if _:
            teacher.set_password('teacher123')
            teacher.save()

        reception, _ = User.objects.get_or_create(
            email='reception@institute.edu.np',
            defaults={'first_name': 'Rita', 'last_name': 'Reception', 'role': User.Role.ADMIN_STAFF},
        )
        if _:
            reception.set_password('reception123')
            reception.save()

        course, _ = Course.objects.get_or_create(
            name='Introduction to Programming',
            defaults={'credits': 3, 'fee': 50000, 'course_type': Course.CourseType.PROGRAM},
        )
        TeacherAssignment.objects.get_or_create(course=course, teacher=teacher, batch=batch)

        fee_head, _ = FeeHead.objects.get_or_create(code='TUITION', defaults={'name': 'Tuition Fee'})
        fee_structure = FeeStructure.objects.filter(
            course=course, batch=batch, fee_head=fee_head,
        ).first()
        if not fee_structure:
            fee_structure = FeeStructure.objects.create(
                course=course, batch=batch, fee_head=fee_head,
                amount=50000, academic_year=year,
            )

        GradePolicy.objects.get_or_create(
            name='Default',
            defaults={'rules': [
                {'min': 90, 'grade': 'A+'}, {'min': 80, 'grade': 'A'},
                {'min': 70, 'grade': 'B+'}, {'min': 60, 'grade': 'B'},
                {'min': 50, 'grade': 'C'}, {'min': 0, 'grade': 'F'},
            ], 'is_active': True},
        )

        for i in range(1, 11):
            email = f'student{i}@institute.edu.np'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Student', 'last_name': str(i),
                    'role': User.Role.STUDENT, 'phone': f'980000000{i:02d}',
                },
            )
            if created:
                user.set_password('student123')
                user.save()
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={'batch': batch, 'date_of_birth': date(2005, 1, 1) + timedelta(days=i * 30)},
            )
            Enrollment.objects.get_or_create(
                student=profile, course=course,
                defaults={'batch': batch, 'status': Enrollment.Status.APPROVED},
            )
            if fee_structure and not StudentFeeAssignment.objects.filter(
                student=profile, fee_structure=fee_structure,
            ).exists():
                StudentFeeAssignment.objects.create(
                    student=profile,
                    fee_structure=fee_structure,
                    total_amount=50000,
                    due_date=date.today() + timedelta(days=30),
                )

        CalendarEvent.objects.get_or_create(
            title='Dashain',
            start_date=date(2025, 10, 20),
            academic_year=year,
            defaults={
                'end_date': date(2025, 10, 24),
                'event_type': CalendarEvent.EventType.PUBLIC_HOLIDAY,
                'description': 'Public holiday',
            },
        )
        CalendarEvent.objects.get_or_create(
            title='Winter term break',
            start_date=date(2025, 12, 20),
            academic_year=year,
            defaults={
                'end_date': date(2026, 1, 5),
                'event_type': CalendarEvent.EventType.TERM_BREAK,
            },
        )

        Announcement.objects.get_or_create(
            title='Welcome to New Academic Year',
            defaults={
                'body': 'Classes begin next Monday. Please check your schedules.',
                'author': super_admin, 'status': Announcement.Status.PUBLISHED,
                'target_roles': ['student', 'teacher'],
            },
        )

        session, _ = AttendanceSession.objects.get_or_create(
            date=date.today(), batch=batch, course=course, period=1,
            defaults={'teacher': teacher, 'shift': morning},
        )
        for profile in StudentProfile.objects.filter(batch=batch)[:5]:
            AttendanceRecord.objects.get_or_create(
                session=session, student=profile,
                defaults={'status': AttendanceRecord.Status.PRESENT, 'source': AttendanceRecord.Source.MANUAL},
            )

        subjects_data = [
            ('CS101', 'Programming Fundamentals', 1),
            ('CS102', 'Data Structures', 1),
            ('MATH101', 'Discrete Mathematics', 1),
        ]
        subjects = []
        for code, name, sem in subjects_data:
            subj, _ = CourseSubject.objects.get_or_create(
                course=course, code=code,
                defaults={'name': name, 'semester': sem, 'max_internal': 40, 'max_external': 60},
            )
            subjects.append(subj)

        term = 'Fall 2025'
        for subj in subjects:
            exam, _ = Exam.objects.get_or_create(
                course=course,
                subject=subj,
                exam_type=Exam.ExamType.MID_TERM,
                term=term,
                defaults={
                    'name': f'{subj.name} — Mid Term ({term})',
                    'max_marks': subj.max_internal + subj.max_external,
                    'is_published': True,
                },
            )
            ResultApproval.objects.get_or_create(
                exam=exam,
                defaults={'stage': ResultApproval.Stage.PUBLISHED, 'approved_by': super_admin},
            )
            for idx, profile in enumerate(StudentProfile.objects.filter(batch=batch)[:5]):
                enr = Enrollment.objects.filter(student=profile, course=course).first()
                MarkEntry.objects.get_or_create(
                    exam=exam, student=profile,
                    defaults={
                        'enrollment': enr,
                        'internal_marks': 18 + idx,
                        'external_marks': 50 + idx * 2,
                        'grade': 'B+',
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            'Demo data seeded. Logins: '
            'admin@institute.edu.np / admin123 (Super Admin), '
            'reception@institute.edu.np / reception123 (Reception), '
            'teacher@institute.edu.np / teacher123, '
            'student1@institute.edu.np / student123'
        ))
