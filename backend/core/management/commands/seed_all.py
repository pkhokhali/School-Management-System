"""
Load demo data for all modules. Safe to re-run (uses get_or_create).

  python manage.py seed_all
  python manage.py seed_all --skip-fees   # faster, skips billing/Fonepay seed
"""
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from announcements.models import Announcement, AnnouncementRead
from announcements.services import dispatch_announcement
from assignments.models import Assignment, AssignmentSubmission
from attendance.models import AttendanceRecord, AttendanceSession
from attendance.services import get_or_create_register, mark_attendance
from biometric_integration.models import BiometricDevice, BiometricUserMap
from communication.models import ChatRoom, Feedback, Forum, ForumPost, LiveClass, Message
from core.models import AuditLog, InstituteSettings
from courses.models import Course, CourseMaterial, CourseSubject, TeacherAssignment
from enrollment.models import Enrollment, EnrollmentHistory
from events.models import CalendarEvent
from leave.models import LeaveApplication, LeaveBalance
from library.models import Book, BookIssue
from notifications.models import DeviceToken, NotificationLog
from students.models import AcademicYear, Batch, Department, Shift, StudentProfile

User = get_user_model()


def _user(email, password, **defaults):
    user, created = User.objects.get_or_create(email=email, defaults=defaults)
    if created:
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Seed demo data for all modules (run seed_demo + fees + extended fixtures)'

    def add_arguments(self, parser):
        parser.add_argument('--skip-fees', action='store_true', help='Skip seed_fee_demo (billing/Fonepay)')

    def handle(self, *args, **options):
        self.stdout.write('Running seed_demo...')
        call_command('seed_demo', verbosity=1)

        if not options['skip_fees']:
            self.stdout.write('Running seed_fee_demo...')
            call_command('seed_fee_demo', verbosity=1)

        self._enable_features()
        ctx = self._load_context()
        self._extend_academic(ctx)
        self._seed_users(ctx)
        self._seed_calendar(ctx)
        self._seed_enrollment(ctx)
        self._seed_attendance(ctx)
        self._seed_announcements(ctx)
        self._seed_library(ctx)
        self._seed_leave(ctx)
        self._seed_assignments(ctx)
        self._seed_communication(ctx)
        self._seed_biometric(ctx)
        self._seed_notifications(ctx)
        self._seed_audit(ctx)

        self.stdout.write(self.style.SUCCESS(self._login_summary()))

    def _enable_features(self):
        solo = InstituteSettings.get_solo()
        flags = {**settings.DEFAULT_FEATURE_FLAGS}
        flags.update({
            'payments_online': True,
            'results_publishing': True,
            'library_management': True,
            'assignments': True,
            'predictive_analytics': True,
            'in_app_chat': True,
            'parent_portal': True,
        })
        solo.feature_flags = flags
        solo.role_channel_access = settings.DEFAULT_ROLE_CHANNEL_ACCESS
        solo.name = 'Valley Technical School (Demo)'
        solo.save(update_fields=['feature_flags', 'role_channel_access', 'name'])
        self.stdout.write('  Feature flags and mobile/web channel access enabled for demo roles.')

    def _load_context(self):
        return {
            'super_admin': User.objects.get(email='admin@institute.edu.np'),
            'teacher': User.objects.get(email='teacher@institute.edu.np'),
            'reception': User.objects.get(email='reception@institute.edu.np'),
            'year': AcademicYear.objects.filter(is_current=True).first(),
            'dept_cs': Department.objects.filter(code='CS').first(),
            'batch': Batch.objects.filter(code='CS-2025-A').first(),
            'shift_morning': Shift.objects.filter(code='MORNING').first(),
            'shift_evening': Shift.objects.filter(code='EVENING').first(),
            'course': Course.objects.first(),
        }

    def _extend_academic(self, ctx):
        dept_mgmt, _ = Department.objects.get_or_create(code='MGMT', defaults={'name': 'Management'})
        evening = ctx['shift_evening']
        year = ctx['year']
        batch_b, _ = Batch.objects.get_or_create(
            code='MGMT-2025-B',
            defaults={
                'name': 'Management Year 1 B',
                'department': dept_mgmt,
                'academic_year': year,
                'semester': 1,
                'shift': evening,
            },
        )
        course2, _ = Course.objects.get_or_create(
            code='BBA-101',
            defaults={
                'name': 'Business Fundamentals',
                'credits': 3,
                'fee': Decimal('45000'),
                'course_type': Course.CourseType.PROGRAM,
                'department': dept_mgmt,
            },
        )
        TeacherAssignment.objects.get_or_create(
            course=course2, teacher=ctx['teacher'], batch=batch_b,
        )
        CourseMaterial.objects.get_or_create(
            course=ctx['course'],
            title='Week 1 Lecture Notes',
            defaults={'material_type': 'note', 'url': 'https://example.edu/demo/notes-week1.pdf'},
        )
        ctx['batch_b'] = batch_b
        ctx['course2'] = course2
        self.stdout.write('  Extra batch, course, teacher assignment, course material.')

    def _seed_users(self, ctx):
        parent = _user(
            'parent@institute.edu.np', 'parent123',
            first_name='Hari', last_name='Parent', role=User.Role.PARENT,
        )
        accountant = _user(
            'accountant@institute.edu.np', 'accountant123',
            first_name='Sita', last_name='Accountant', role=User.Role.ADMIN_STAFF,
        )
        ctx['parent'] = parent
        ctx['accountant'] = accountant
        self.stdout.write('  Parent + accountant users.')

    def _seed_calendar(self, ctx):
        year = ctx['year']
        CalendarEvent.objects.get_or_create(
            title='Mid-term exam week',
            start_date=date.today() + timedelta(days=14),
            academic_year=year,
            defaults={
                'end_date': date.today() + timedelta(days=18),
                'event_type': CalendarEvent.EventType.EXAM,
                'description': 'Internal assessments',
            },
        )
        CalendarEvent.objects.get_or_create(
            title='College picnic',
            start_date=date.today() + timedelta(days=30),
            academic_year=year,
            defaults={
                'end_date': date.today() + timedelta(days=30),
                'event_type': CalendarEvent.EventType.EVENT,
            },
        )
        self.stdout.write('  Calendar events (exam, event).')

    def _seed_enrollment(self, ctx):
        batch = ctx['batch']
        course2 = ctx.get('course2')
        profiles = list(StudentProfile.objects.filter(batch=batch).order_by('id'))
        if len(profiles) >= 10 and course2:
            p = profiles[9]
            enr, created = Enrollment.objects.get_or_create(
                student=p, course=course2,
                defaults={'batch': ctx['batch_b'], 'status': Enrollment.Status.PENDING},
            )
            if created:
                EnrollmentHistory.objects.create(
                    enrollment=enr, status=Enrollment.Status.PENDING,
                    note='Demo pending approval', changed_by=ctx['reception'],
                )
        if len(profiles) >= 8:
            enr_drop, _ = Enrollment.objects.get_or_create(
                student=profiles[7], course=ctx['course'],
                defaults={'batch': batch, 'status': Enrollment.Status.DROPPED, 'drop_reason': 'Demo transfer'},
            )
            if enr_drop.status != Enrollment.Status.DROPPED:
                enr_drop.status = Enrollment.Status.DROPPED
                enr_drop.save(update_fields=['status', 'drop_reason'])
        self.stdout.write('  Enrollment pending + dropped samples.')

    def _seed_attendance(self, ctx):
        teacher = ctx['teacher']
        batch = ctx['batch']
        course = ctx['course']
        morning = ctx['shift_morning']
        today = date.today()
        yesterday = today - timedelta(days=1)

        reg_today, _ = get_or_create_register(today, batch.id, course.id, period=1, teacher=teacher, shift_id=morning.id if morning else None)
        reg_p2, _ = get_or_create_register(today, batch.id, course.id, period=2, teacher=teacher, shift_id=morning.id if morning else None)
        reg_yesterday, _ = get_or_create_register(yesterday, batch.id, course.id, period=1, teacher=teacher, shift_id=morning.id if morning else None)

        profiles = list(StudentProfile.objects.filter(batch=batch)[:8])
        for idx, profile in enumerate(profiles):
            status = AttendanceRecord.Status.PRESENT
            if idx == 5:
                status = AttendanceRecord.Status.ABSENT
            elif idx == 6:
                status = AttendanceRecord.Status.LATE
            mark_attendance(reg_today, profile, status, AttendanceRecord.Source.MANUAL, teacher)

        if len(profiles) >= 2:
            mark_attendance(reg_yesterday, profiles[0], AttendanceRecord.Status.PRESENT, AttendanceRecord.Source.MANUAL, teacher)
            mark_attendance(reg_yesterday, profiles[1], AttendanceRecord.Status.ABSENT, AttendanceRecord.Source.MANUAL, teacher)
            mark_attendance(reg_p2, profiles[0], AttendanceRecord.Status.PRESENT, AttendanceRecord.Source.QR, teacher)

        if len(profiles) >= 1:
            mark_attendance(reg_today, profiles[0], AttendanceRecord.Status.PRESENT, AttendanceRecord.Source.QR, teacher)

        self.stdout.write('  Class registers (today P1/P2, yesterday) + mixed statuses.')

    def _seed_announcements(self, ctx):
        dept = ctx['dept_cs']
        batch = ctx['batch']
        shift = ctx['shift_morning']
        super_admin = ctx['super_admin']
        teacher = ctx['teacher']

        draft, _ = Announcement.objects.get_or_create(
            title='Draft: Library hours change',
            defaults={
                'body': 'Not yet published — for editor testing.',
                'author': super_admin,
                'status': Announcement.Status.DRAFT,
                'channels': [Announcement.Channel.WEB],
            },
        )

        published, created = Announcement.objects.get_or_create(
            title='Fee payment deadline reminder',
            defaults={
                'body': 'Please clear semester fees by the due date to avoid late fees.',
                'author': ctx['reception'],
                'status': Announcement.Status.PUBLISHED,
                'channels': [Announcement.Channel.WEB, Announcement.Channel.EMAIL, Announcement.Channel.MOBILE],
                'target_roles': ['student'],
                'published_at': timezone.now(),
                'is_important': True,
            },
        )
        published.target_batches.add(batch)
        if created:
            dispatch_announcement(published)

        dept_ann, _ = Announcement.objects.get_or_create(
            title='CS department workshop',
            defaults={
                'body': 'All CS students: workshop on Saturday 10 AM.',
                'author': teacher,
                'status': Announcement.Status.PUBLISHED,
                'channels': [Announcement.Channel.WEB, Announcement.Channel.SMS],
                'published_at': timezone.now(),
            },
        )
        dept_ann.target_departments.add(dept)
        if shift:
            dept_ann.target_shifts.add(shift)

        for user in User.objects.filter(role=User.Role.STUDENT)[:3]:
            AnnouncementRead.objects.get_or_create(announcement=published, user=user)

        self.stdout.write('  Announcements (draft, published, reads, delivery).')

    def _seed_library(self, ctx):
        books = [
            ('Clean Code', '9780132350884', 3),
            ('Introduction to Algorithms', '9780262033848', 2),
            ('Nepal Constitution', '9789937597000', 5),
        ]
        profile = StudentProfile.objects.filter(batch=ctx['batch']).first()
        for title, isbn, copies in books:
            book, _ = Book.objects.get_or_create(
                isbn=isbn,
                defaults={'title': title, 'copies_total': copies, 'copies_available': max(0, copies - 1)},
            )
            if profile and not BookIssue.objects.filter(book=book, student=profile, returned_at__isnull=True).exists():
                BookIssue.objects.create(
                    book=book, student=profile,
                    due_date=date.today() + timedelta(days=14),
                )
        self.stdout.write('  Library books + active issue.')

    def _seed_leave(self, ctx):
        teacher = ctx['teacher']
        LeaveBalance.objects.get_or_create(user=teacher, defaults={'annual_days': 20, 'used_days': 3})
        LeaveApplication.objects.get_or_create(
            user=teacher,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            defaults={
                'reason': 'Family function (demo)',
                'status': LeaveApplication.Status.PENDING,
            },
        )
        LeaveApplication.objects.get_or_create(
            user=ctx['reception'],
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() - timedelta(days=3),
            defaults={
                'reason': 'Approved leave sample',
                'status': LeaveApplication.Status.APPROVED,
                'approved_by': ctx['super_admin'],
            },
        )
        self.stdout.write('  Leave balances and applications.')

    def _seed_assignments(self, ctx):
        course = ctx['course']
        teacher = ctx['teacher']
        assignment, _ = Assignment.objects.get_or_create(
            course=course,
            title='Assignment 1: Hello World',
            defaults={
                'description': 'Submit a working program with comments.',
                'due_date': timezone.now() + timedelta(days=7),
                'max_marks': Decimal('20'),
                'created_by': teacher,
            },
        )
        for profile in StudentProfile.objects.filter(batch=ctx['batch'])[:3]:
            AssignmentSubmission.objects.get_or_create(
                assignment=assignment,
                student=profile,
                defaults={
                    'file': SimpleUploadedFile(
                        f'submission_{profile.enrollment_number}.txt',
                        b'print("hello from demo student")',
                    ),
                    'marks': Decimal('16') + Decimal(profile.id % 3),
                    'feedback': 'Good work (demo).',
                },
            )
        self.stdout.write('  Assignments + submissions.')

    def _seed_communication(self, ctx):
        course = ctx['course']
        teacher = ctx['teacher']
        student_user = User.objects.filter(email='student1@institute.edu.np').first()

        room, _ = ChatRoom.objects.get_or_create(name='Teacher — Student1 demo')
        if student_user:
            room.participants.add(teacher, student_user)
            Message.objects.get_or_create(
                room=room, sender=teacher,
                defaults={'content': 'Please see me after class regarding your assignment.'},
            )

        forum, _ = Forum.objects.get_or_create(
            course=course, title='General Q&A',
            defaults={'created_by': teacher},
        )
        ForumPost.objects.get_or_create(
            forum=forum, author=student_user or teacher,
            defaults={'content': 'When is the next lab session? (demo post)'},
        )

        LiveClass.objects.get_or_create(
            course=course,
            title='Live revision session',
            defaults={
                'meeting_url': 'https://zoom.us/j/demo-meeting-id',
                'scheduled_at': timezone.now() + timedelta(days=2),
            },
        )

        if student_user:
            Feedback.objects.get_or_create(
                user=student_user,
                target_type='course',
                target_id=course.id,
                defaults={'rating': 4, 'comment': 'Engaging lectures (demo).'},
            )
        self.stdout.write('  Chat, forum, live class, feedback.')

    def _seed_biometric(self, ctx):
        course = ctx['course']
        device, _ = BiometricDevice.objects.get_or_create(
            device_id='BIO-DEMO-001',
            defaults={
                'name': 'Main gate scanner',
                'location': 'Reception entrance',
                'default_course': course,
                'default_period': 1,
            },
        )
        for profile in StudentProfile.objects.filter(batch=ctx['batch'])[:4]:
            if profile.user_id:
                BiometricUserMap.objects.get_or_create(
                    device=device,
                    device_user_id=f'DEV-{profile.enrollment_number}',
                    defaults={'user': profile.user, 'student': profile},
                )
        self.stdout.write('  Biometric device + student maps.')

    def _seed_notifications(self, ctx):
        student = User.objects.filter(email='student1@institute.edu.np').first()
        if student:
            DeviceToken.objects.get_or_create(
                user=student,
                token='demo-fcm-token-student1',
                defaults={'platform': 'android'},
            )
            if not NotificationLog.objects.filter(
                user=student, title='Fee payment deadline reminder',
            ).exists():
                NotificationLog.objects.create(
                    user=student,
                    title='Fee payment deadline reminder',
                    body='Please clear semester fees by the due date.',
                    data={'announcement_id': 0, 'channel': 'mobile'},
                )
        self.stdout.write('  Device token + notification log.')

    def _seed_audit(self, ctx):
        AuditLog.objects.get_or_create(
            user=ctx['super_admin'],
            action='update',
            model_name='InstituteSettings',
            object_id='1',
            defaults={'changes': {'feature_flags': 'enabled demo modules'}},
        )
        self.stdout.write('  Sample audit log entry.')

    def _login_summary(self):
        return (
            '\n=== Demo data ready ===\n'
            'Super Admin:    admin@institute.edu.np / admin123\n'
            'Reception:      reception@institute.edu.np / reception123\n'
            'Accountant:     accountant@institute.edu.np / accountant123\n'
            'Teacher:        teacher@institute.edu.np / teacher123\n'
            'Student:        student1@institute.edu.np / student123 (also student2…10)\n'
            'Parent:         parent@institute.edu.np / parent123\n'
            '\nModules: students, courses, enrollment, attendance, calendar, fees (if not --skip-fees), '
            'results, announcements, library, leave, assignments, communication, biometric, notifications.\n'
            'Enable features are ON in institute settings for testing.\n'
        )
