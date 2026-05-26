from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from core.mixins import FeatureFlagViewMixin
from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['created_by']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = ['submitted_at']


class AssignmentFeatureMixin(FeatureFlagViewMixin):
    feature_key = 'assignments'


class AssignmentViewSet(AssignmentFeatureMixin, viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('course')
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignmentSubmissionViewSet(AssignmentFeatureMixin, viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related('assignment', 'student')
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
