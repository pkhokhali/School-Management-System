from django.core.cache import cache
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.openapi import DetailResponseSerializer
from attendance.models import AttendanceRecord
from enrollment.models import Enrollment
from fees.models import Payment, StudentFeeAssignment
from announcements.models import AnnouncementRead
from results.models import MarkEntry
from students.models import StudentProfile
from .serializers import StudentTimelineSerializer


class StudentTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: StudentTimelineSerializer, 404: DetailResponseSerializer})
    def get(self, request, student_id):
        cache_key = f'student_timeline_{student_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        try:
            student = StudentProfile.objects.get(pk=student_id)
        except StudentProfile.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        events = []

        for e in Enrollment.objects.filter(student=student).order_by('-created_at'):
            events.append({
                'type': 'enrollment',
                'date': e.created_at.isoformat(),
                'title': f'Enrolled in {e.course.name}',
                'status': e.status,
            })

        for p in Payment.objects.filter(student_fee__student=student).order_by('-created_at'):
            events.append({
                'type': 'payment',
                'date': p.created_at.isoformat(),
                'title': f'Payment {p.receipt_id}',
                'amount': str(p.amount),
                'mode': p.mode,
            })

        total_att = AttendanceRecord.objects.filter(student=student).count()
        present = AttendanceRecord.objects.filter(
            student=student, status=AttendanceRecord.Status.PRESENT,
        ).count()
        pct = (present / total_att * 100) if total_att else 0
        events.append({
            'type': 'attendance_summary',
            'title': f'Attendance {pct:.1f}%',
            'present': present,
            'total': total_att,
        })

        for m in MarkEntry.objects.filter(student=student).select_related('exam'):
            events.append({
                'type': 'result',
                'date': m.exam.id,
                'title': f'{m.exam.name}: {m.grade}',
            })

        events.sort(key=lambda x: str(x.get('date', '')), reverse=True)
        data = {'student_id': student_id, 'events': events}
        cache.set(cache_key, data, 300)
        return Response(data)
