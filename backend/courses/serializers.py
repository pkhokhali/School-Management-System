from rest_framework import serializers
from .models import Course, CourseMaterial, CoursePrerequisite, CourseSubject, SyllabusFile, TeacherAssignment


class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    teachers_count = serializers.SerializerMethodField()
    materials_count = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    syllabus_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'code', 'course_type', 'department', 'department_name', 'level',
            'duration_months', 'duration_years', 'total_semesters', 'duration_display',
            'credits', 'fee', 'max_enrollment', 'delivery_mode', 'is_active',
            'teachers_count', 'materials_count', 'description', 'syllabus_pdf_url',
        ]
        read_only_fields = ['code']

    def get_syllabus_pdf_url(self, obj):
        if obj.syllabus_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.syllabus_pdf.url)
            return obj.syllabus_pdf.url
        return None

    def get_teachers_count(self, obj):
        return obj.teachers.count()

    def get_materials_count(self, obj):
        return obj.materials.count()

    def get_duration_display(self, obj):
        return f'{obj.duration_years} yr / {obj.duration_months} mo / {obj.total_semesters} sem'


class CourseDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    materials = serializers.SerializerMethodField()
    syllabi = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    prerequisites = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_materials(self, obj):
        return CourseMaterialSerializer(obj.materials.all(), many=True).data

    def get_syllabi(self, obj):
        return SyllabusFileSerializer(obj.syllabi.all(), many=True).data

    def get_teachers(self, obj):
        return TeacherAssignmentSerializer(obj.teachers.select_related('teacher', 'batch'), many=True).data

    def get_prerequisites(self, obj):
        return [
            {'id': p.prerequisite_id, 'code': p.prerequisite.code, 'name': p.prerequisite.name}
            for p in obj.prerequisites.select_related('prerequisite')
        ]


class CourseSerializer(CourseListSerializer):
    """Default list/create/update — course code is auto-generated on create."""

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'learning_outcomes', 'syllabus_pdf', 'created_at', 'updated_at',
        ]
        read_only_fields = ['code', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data.pop('code', None)
        return super().create(validated_data)


class SyllabusFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabusFile
        fields = '__all__'


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = '__all__'


class CourseSubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)

    class Meta:
        model = CourseSubject
        fields = [
            'id', 'course', 'course_name', 'course_code', 'code', 'name', 'semester',
            'credit_hours', 'max_internal', 'max_external', 'is_active',
        ]


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True, allow_null=True)

    class Meta:
        model = TeacherAssignment
        fields = '__all__'
