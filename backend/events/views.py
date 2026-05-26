from datetime import date

from calendar import monthrange

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsInstituteAdmin, ReadOnlyOrInstituteAdmin
from students.models import AcademicYear
from .models import CalendarEvent
from .serializers import (
    BulkUploadSerializer,
    CalendarEventSerializer,
    MarkHolidayRangeSerializer,
)
from .services import count_working_days, events_in_range, is_institute_holiday, parse_bulk_csv


class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.select_related('academic_year', 'created_by')
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['event_type', 'academic_year', 'start_date']

    def get_queryset(self):
        qs = super().get_queryset()
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        if from_date and to_date:
            qs = qs.filter(start_date__lte=to_date, end_date__gte=from_date)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(request=MarkHolidayRangeSerializer, responses={201: CalendarEventSerializer})
    @action(detail=False, methods=['post'], url_path='mark-holiday-range')
    def mark_holiday_range(self, request):
        serializer = MarkHolidayRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        academic_year = None
        if data.get('academic_year'):
            academic_year = AcademicYear.objects.filter(pk=data['academic_year']).first()
        event = CalendarEvent.objects.create(
            academic_year=academic_year,
            title=data['title'],
            event_type=data['event_type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            description=data.get('description', ''),
            created_by=request.user,
        )
        return Response(CalendarEventSerializer(event).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=BulkUploadSerializer)
    @action(
        detail=False,
        methods=['post'],
        url_path='bulk-upload',
        parser_classes=[MultiPartParser, FormParser],
    )
    def bulk_upload(self, request):
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = parse_bulk_csv(
            serializer.validated_data['file'],
            academic_year_id=serializer.validated_data.get('academic_year'),
            created_by=request.user,
        )
        return Response(result)


class CalendarMonthView(APIView):
    """Events and holiday summary for a calendar month."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get('year', timezone.localdate().year))
            month = int(request.query_params.get('month', timezone.localdate().month))
        except (TypeError, ValueError):
            return Response({'detail': 'year and month required'}, status=status.HTTP_400_BAD_REQUEST)

        academic_year_id = request.query_params.get('academic_year')
        from_date = date(year, month, 1)
        to_date = date(year, month, monthrange(year, month)[1])

        ay_id = int(academic_year_id) if academic_year_id else None
        events = events_in_range(from_date, to_date, ay_id)
        summary = count_working_days(from_date, to_date, ay_id)

        return Response({
            'year': year,
            'month': month,
            'from_date': from_date.isoformat(),
            'to_date': to_date.isoformat(),
            'events': CalendarEventSerializer(events, many=True).data,
            'summary': summary,
        })


class IsWorkingDayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        check = request.query_params.get('date')
        if not check:
            return Response({'detail': 'date query param required (YYYY-MM-DD)'}, status=400)
        try:
            check_date = date.fromisoformat(check)
        except ValueError:
            return Response({'detail': 'Invalid date'}, status=400)
        ay = request.query_params.get('academic_year')
        ay_id = int(ay) if ay else None
        holiday = is_institute_holiday(check_date, ay_id)
        return Response({
            'date': check_date.isoformat(),
            'is_holiday': holiday,
            'is_working_day': not holiday,
        })


class CurrentAcademicYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = AcademicYear.objects.filter(is_current=True).first()
        if not year:
            year = AcademicYear.objects.order_by('-start_date').first()
        if not year:
            return Response({'detail': 'No academic year configured'}, status=404)
        from students.serializers import AcademicYearSerializer
        return Response(AcademicYearSerializer(year).data)
