# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_course_subject'),
        ('enrollment', '0002_enrollment_ordering'),
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='subject',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='exams', to='courses.coursesubject',
            ),
        ),
        migrations.AddField(
            model_name='markentry',
            name='enrollment',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='marks', to='enrollment.enrollment',
            ),
        ),
        migrations.AddField(
            model_name='markentry',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddConstraint(
            model_name='exam',
            constraint=models.UniqueConstraint(
                condition=models.Q(('subject__isnull', False)),
                fields=('course', 'subject', 'exam_type', 'term'),
                name='unique_exam_per_subject_term',
            ),
        ),
    ]
