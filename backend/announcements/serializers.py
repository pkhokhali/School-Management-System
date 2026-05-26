from rest_framework import serializers
from .models import Announcement, AnnouncementRead


class AnnouncementSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    target_department_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Announcement.target_departments.field.related_model.objects.all(),
        source='target_departments', required=False,
    )
    target_batch_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Announcement.target_batches.field.related_model.objects.all(),
        source='target_batches', required=False,
    )
    target_shift_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Announcement.target_shifts.field.related_model.objects.all(),
        source='target_shifts', required=False,
    )

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'body', 'author', 'author_name', 'channels',
            'target_roles', 'target_all_students', 'target_all_teachers', 'target_all_admin_staff',
            'target_department_ids', 'target_batch_ids', 'target_shift_ids',
            'attachment', 'is_important', 'status', 'publish_at', 'published_at', 'created_at', 'is_read',
        ]
        read_only_fields = ['author', 'published_at', 'created_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return AnnouncementRead.objects.filter(announcement=obj, user=request.user).exists()

    def create(self, validated_data):
        depts = validated_data.pop('target_departments', [])
        batches = validated_data.pop('target_batches', [])
        shifts = validated_data.pop('target_shifts', [])
        ann = Announcement.objects.create(**validated_data)
        if depts:
            ann.target_departments.set(depts)
        if batches:
            ann.target_batches.set(batches)
        if shifts:
            ann.target_shifts.set(shifts)
        return ann

    def update(self, instance, validated_data):
        depts = validated_data.pop('target_departments', None)
        batches = validated_data.pop('target_batches', None)
        shifts = validated_data.pop('target_shifts', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if depts is not None:
            instance.target_departments.set(depts)
        if batches is not None:
            instance.target_batches.set(batches)
        if shifts is not None:
            instance.target_shifts.set(shifts)
        return instance


class AnnouncementReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementRead
        fields = '__all__'
