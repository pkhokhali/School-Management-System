import csv
import io
from datetime import date, timedelta

from django.db import transaction

from students.models import AcademicYear
from .models import CalendarEvent

HOLIDAY_TYPES = frozenset({
    CalendarEvent.EventType.PUBLIC_HOLIDAY,
    CalendarEvent.EventType.HOLIDAY,
    CalendarEvent.EventType.TERM_BREAK,
})

CSV_HEADERS = ('title', 'event_type', 'start_date', 'end_date', 'description')


def events_in_range(from_date: date, to_date: date, academic_year_id=None):
    qs = CalendarEvent.objects.filter(start_date__lte=to_date, end_date__gte=from_date)
    if academic_year_id:
        qs = qs.filter(academic_year_id=academic_year_id)
    return qs.select_related('academic_year').order_by('start_date', 'title')


def is_institute_holiday(check_date: date, academic_year_id=None) -> bool:
    qs = CalendarEvent.objects.filter(
        start_date__lte=check_date,
        end_date__gte=check_date,
        event_type__in=HOLIDAY_TYPES,
    )
    if academic_year_id:
        qs = qs.filter(academic_year_id=academic_year_id)
    return qs.exists()


def iter_dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def count_working_days(from_date: date, to_date: date, academic_year_id=None) -> dict:
    """Working days = calendar days minus holiday-type events (weekends not excluded by default)."""
    total = (to_date - from_date).days + 1
    holiday_dates = set()
    for event in events_in_range(from_date, to_date, academic_year_id):
        if event.event_type in HOLIDAY_TYPES:
            for d in iter_dates(event.start_date, event.end_date):
                if from_date <= d <= to_date:
                    holiday_dates.add(d)
    return {
        'total_days': total,
        'holiday_days': len(holiday_dates),
        'working_days': total - len(holiday_dates),
        'holiday_dates': sorted(d.isoformat() for d in holiday_dates),
    }


def parse_bulk_csv(file_obj, academic_year_id=None, created_by=None) -> dict:
    """Import calendar rows from CSV. Returns created, skipped, errors."""
    if hasattr(file_obj, 'read'):
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8-sig')
    else:
        content = str(file_obj)

    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return {'created': [], 'skipped': [], 'errors': ['Empty file or missing header row']}

    normalized_headers = {h.strip().lower(): h for h in reader.fieldnames if h}
    missing = [h for h in CSV_HEADERS if h not in normalized_headers]
    if missing:
        return {
            'created': [],
            'skipped': [],
            'errors': [f'Missing columns: {", ".join(missing)}. Expected: {", ".join(CSV_HEADERS)}'],
        }

    academic_year = None
    if academic_year_id:
        try:
            academic_year = AcademicYear.objects.get(pk=academic_year_id)
        except AcademicYear.DoesNotExist:
            return {'created': [], 'skipped': [], 'errors': ['Academic year not found']}

    created = []
    skipped = []
    errors = []

    with transaction.atomic():
        for line_no, row in enumerate(reader, start=2):
            title = (row.get(normalized_headers['title']) or '').strip()
            event_type = (row.get(normalized_headers['event_type']) or '').strip().lower()
            start_s = (row.get(normalized_headers['start_date']) or '').strip()
            end_s = (row.get(normalized_headers['end_date']) or '').strip() or start_s
            description = (row.get(normalized_headers['description']) or '').strip()

            if not title and not start_s:
                continue
            if not title:
                errors.append(f'Line {line_no}: title is required')
                continue
            if event_type not in CalendarEvent.EventType.values:
                errors.append(
                    f'Line {line_no}: invalid event_type "{event_type}"'
                )
                continue
            try:
                start_date = date.fromisoformat(start_s)
                end_date = date.fromisoformat(end_s)
            except ValueError:
                errors.append(f'Line {line_no}: invalid date (use YYYY-MM-DD)')
                continue
            if end_date < start_date:
                end_date = start_date

            exists = CalendarEvent.objects.filter(
                title=title,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                academic_year=academic_year,
            ).exists()
            if exists:
                skipped.append({'line': line_no, 'title': title, 'reason': 'Duplicate'})
                continue

            event = CalendarEvent.objects.create(
                academic_year=academic_year,
                title=title,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                description=description,
                created_by=created_by,
            )
            created.append({'id': event.id, 'title': event.title, 'line': line_no})

    return {'created': created, 'skipped': skipped, 'errors': errors}
