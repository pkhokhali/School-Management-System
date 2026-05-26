from rest_framework import serializers

from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    is_holiday_type = serializers.BooleanField(read_only=True)

    class Meta:
        model = CalendarEvent
        fields = [
            'id',
            'academic_year',
            'academic_year_name',
            'title',
            'event_type',
            'start_date',
            'end_date',
            'description',
            'google_calendar_id',
            'created_by',
            'created_by_name',
            'is_holiday_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class MarkHolidayRangeSerializer(serializers.Serializer):
    academic_year = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=200)
    event_type = serializers.ChoiceField(
        choices=[
            CalendarEvent.EventType.PUBLIC_HOLIDAY,
            CalendarEvent.EventType.HOLIDAY,
            CalendarEvent.EventType.TERM_BREAK,
        ],
        default=CalendarEvent.EventType.HOLIDAY,
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})
        return attrs


class BulkUploadSerializer(serializers.Serializer):
    academic_year = serializers.IntegerField(required=False, allow_null=True)
    file = serializers.FileField()
