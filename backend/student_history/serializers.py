from rest_framework import serializers


class StudentTimelineSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    events = serializers.ListField(child=serializers.DictField())
