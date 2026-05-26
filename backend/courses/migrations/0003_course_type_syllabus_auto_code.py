from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_course_admin_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_type',
            field=models.CharField(
                choices=[
                    ('program', 'Degree / Program'),
                    ('short_term', 'Short Term'),
                    ('internship', 'Internship'),
                ],
                default='program',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='syllabus_pdf',
            field=models.FileField(blank=True, null=True, upload_to='syllabi/courses/'),
        ),
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(blank=True, max_length=30, unique=True),
        ),
    ]
