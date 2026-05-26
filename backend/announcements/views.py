from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import ReadOnlyOrInstituteAdmin
from notifications.models import NotificationLog
from .models import Announcement, AnnouncementRead
from .serializers import AnnouncementSerializer
from .services import dispatch_announcement, resolve_announcement_recipients

DeliveryChannelStatSerializer = inline_serializer(
    name='DeliveryChannelStat',
    fields={
        'channel': serializers.CharField(),
        'sent': serializers.IntegerField(),
        'read': serializers.IntegerField(),
    },
    many=True,
)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.prefetch_related(
        'target_batches', 'target_departments', 'target_shifts',
    ).all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrInstituteAdmin]
    filterset_fields = ['status', 'is_important']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role not in ('super_admin', 'admin_staff'):
            qs = qs.filter(status=Announcement.Status.PUBLISHED)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        ann = self.get_object()
        ann.status = Announcement.Status.PUBLISHED
        ann.published_at = timezone.now()
        ann.save()
        count = dispatch_announcement(ann)
        data = AnnouncementSerializer(ann, context={'request': request}).data
        data['recipients_notified'] = count
        return Response(data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        ann = self.get_object()
        ann.status = Announcement.Status.ARCHIVED
        ann.save(update_fields=['status'])
        return Response(AnnouncementSerializer(ann, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        ann = self.get_object()
        AnnouncementRead.objects.get_or_create(announcement=ann, user=request.user)
        return Response({'detail': 'Marked read'})

    @extend_schema(responses={200: DeliveryChannelStatSerializer})
    @action(detail=True, methods=['get'], url_path='delivery-report')
    def delivery_report(self, request, pk=None):
        ann = self.get_object()
        if ann.status != Announcement.Status.PUBLISHED:
            return Response({'detail': 'Available for published announcements only.'}, status=status.HTTP_400_BAD_REQUEST)

        channels = ann.channels or ['web']
        users = resolve_announcement_recipients(ann)
        logs = NotificationLog.objects.filter(data__announcement_id=ann.id)
        read_logs = logs.filter(is_read=True).count()
        announcement_reads = AnnouncementRead.objects.filter(announcement=ann).count()

        stats = []
        for channel in channels:
            if channel in ('web', 'mobile'):
                ch_logs = logs.filter(data__channel=channel)
                sent = ch_logs.count()
                read = ch_logs.filter(is_read=True).count()
            elif channel == 'email':
                sent = sum(1 for u in users if u.email)
                read = 0
            elif channel == 'sms':
                sent = sum(1 for u in users if getattr(u, 'phone', None))
                read = 0
            else:
                sent = 0
                read = 0
            stats.append({'channel': channel, 'sent': sent, 'read': read})

        return Response({
            'channels': stats,
            'total_recipients': len(users),
            'announcement_reads': announcement_reads,
            'in_app_read': read_logs,
        })
