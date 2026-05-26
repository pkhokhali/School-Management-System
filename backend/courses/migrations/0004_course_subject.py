# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_type_syllabus_auto_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=200)),
                ('semester', models.PositiveSmallIntegerField(default=1)),
                ('credit_hours', models.DecimalField(decimal_places=1, default=3, max_digits=4)),
                ('max_internal', models.DecimalField(decimal_places=2, default=40, max_digits=6)),
                ('max_external', models.DecimalField(decimal_places=2, default=60, max_digits=6)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='courses.course')),
            ],
            options={
                'ordering': ['semester', 'code'],
                'unique_together': {('course', 'code')},
            },
        ),
    ]
