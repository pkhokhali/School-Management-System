from rest_framework import serializers

from enrollment.models import Enrollment
from .models import Exam, GradePolicy, MarkEntry, ResultApproval
from .services import calculate_grade


class GradePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradePolicy
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True, allow_null=True)

    class Meta:
        model = Exam
        fields = '__all__'


class MarkEntrySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    enrollment_number = serializers.CharField(source='student.enrollment_number', read_only=True)
    course_name = serializers.CharField(source='exam.course.name', read_only=True)
    course_code = serializers.CharField(source='exam.course.code', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True, allow_null=True)
    subject_code = serializers.CharField(source='exam.subject.code', read_only=True, allow_null=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    exam_type = serializers.CharField(source='exam.exam_type', read_only=True)
    term = serializers.CharField(source='exam.term', read_only=True)
    is_published = serializers.BooleanField(source='exam.is_published', read_only=True)
    total_marks = serializers.SerializerMethodField()

    class Meta:
        model = MarkEntry
        fields = [
            'id', 'exam', 'student', 'enrollment', 'internal_marks', 'external_marks', 'grade',
            'entered_by', 'updated_at', 'student_name', 'enrollment_number', 'course_name', 'course_code',
            'subject_name', 'subject_code', 'exam_name', 'exam_type', 'term', 'is_published', 'total_marks',
        ]
        read_only_fields = ['entered_by', 'grade', 'updated_at']

    def get_total_marks(self, obj):
        return float(obj.internal_marks) + float(obj.external_marks)

    def validate(self, attrs):
        exam = attrs.get('exam') or (self.instance.exam if self.instance else None)
        student = attrs.get('student') or (self.instance.student if self.instance else None)
        if exam and student:
            if not Enrollment.objects.filter(
                student=student,
                course_id=exam.course_id,
                status=Enrollment.Status.APPROVED,
            ).exists():
                raise serializers.ValidationError(
                    'Student must have an approved enrollment in this program.',
                )
        internal = attrs.get('internal_marks', getattr(self.instance, 'internal_marks', 0))
        external = attrs.get('external_marks', getattr(self.instance, 'external_marks', 0))
        if exam and exam.subject_id:
            subj = exam.subject
            if float(internal) > float(subj.max_internal):
                raise serializers.ValidationError({'internal_marks': 'Exceeds subject maximum.'})
            if float(external) > float(subj.max_external):
                raise serializers.ValidationError({'external_marks': 'Exceeds subject maximum.'})
        return attrs


class MarkSheetEntrySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    internal_marks = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    external_marks = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)


class MarkSheetSaveSerializer(serializers.Serializer):
    course = serializers.IntegerField()
    semester = serializers.IntegerField(min_value=1)
    exam_type = serializers.ChoiceField(choices=Exam.ExamType.choices)
    term = serializers.CharField(max_length=50)
    batch = serializers.IntegerField(required=False, allow_null=True)
    entries = MarkSheetEntrySerializer(many=True)


class MarkSheetQuerySerializer(serializers.Serializer):
    course = serializers.IntegerField()
    semester = serializers.IntegerField(min_value=1)
    exam_type = serializers.ChoiceField(choices=Exam.ExamType.choices)
    term = serializers.CharField(max_length=50)
    batch = serializers.IntegerField(required=False, allow_null=True)


class ResultApprovalSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    course_name = serializers.CharField(source='exam.course.name', read_only=True)
    course_code = serializers.CharField(source='exam.course.code', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True, allow_null=True)
    exam_type = serializers.CharField(source='exam.exam_type', read_only=True)
    term = serializers.CharField(source='exam.term', read_only=True)
    is_published = serializers.BooleanField(source='exam.is_published', read_only=True)
    marks_count = serializers.SerializerMethodField()
    stage_label = serializers.SerializerMethodField()
    next_stage = serializers.SerializerMethodField()

    class Meta:
        model = ResultApproval
        fields = [
            'id', 'exam', 'stage', 'stage_label', 'next_stage', 'approved_by', 'updated_at',
            'exam_name', 'course_name', 'course_code', 'subject_name', 'exam_type', 'term',
            'is_published', 'marks_count',
        ]
        read_only_fields = ['approved_by', 'updated_at']

    def get_marks_count(self, obj):
        return obj.exam.marks.count()

    def get_stage_label(self, obj):
        return dict(ResultApproval.Stage.choices).get(obj.stage, obj.stage)

    def get_next_stage(self, obj):
        stages = ['teacher', 'hod', 'admin', 'published']
        idx = stages.index(obj.stage) if obj.stage in stages else 0
        if idx < len(stages) - 1:
            return stages[idx + 1]
        return None


class ExamSessionSerializer(serializers.ModelSerializer):
    """Exam row for publish/approval UI."""

    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True, allow_null=True)
    marks_count = serializers.SerializerMethodField()
    approval_id = serializers.SerializerMethodField()
    approval_stage = serializers.SerializerMethodField()
    approval_stage_label = serializers.SerializerMethodField()
    next_stage = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type', 'term', 'course', 'course_name', 'subject', 'subject_name',
            'subject_code', 'is_published', 'marks_count', 'approval_id', 'approval_stage',
            'approval_stage_label', 'next_stage',
        ]

    def get_marks_count(self, obj):
        return obj.marks.count()

    def _approval(self, obj):
        return getattr(obj, 'approval', None)

    def get_approval_id(self, obj):
        a = self._approval(obj)
        return a.id if a else None

    def get_approval_stage(self, obj):
        a = self._approval(obj)
        if a:
            return a.stage
        return None if obj.is_published else 'draft'

    def get_approval_stage_label(self, obj):
        stage = self.get_approval_stage(obj)
        if stage == 'draft':
            return 'Marks entered (not submitted)'
        if stage:
            return dict(ResultApproval.Stage.choices).get(stage, stage)
        return '—'

    def get_next_stage(self, obj):
        a = self._approval(obj)
        if not a or obj.is_published:
            return None
        stages = ['teacher', 'hod', 'admin', 'published']
        idx = stages.index(a.stage) if a.stage in stages else 0
        if idx < len(stages) - 1:
            return stages[idx + 1]
        return None
