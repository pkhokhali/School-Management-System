# Generated migration for course admin fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='delivery_mode',
            field=models.CharField(
                choices=[('on_campus', 'On Campus'), ('online', 'Online'), ('hybrid', 'Hybrid')],
                default='on_campus',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='courses',
                to='students.department',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='duration_years',
            field=models.DecimalField(decimal_places=1, default=4, max_digits=3),
        ),
        migrations.AddField(
            model_name='course',
            name='learning_outcomes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.CharField(
                choices=[
                    ('certificate', 'Certificate'),
                    ('diploma', 'Diploma'),
                    ('bachelor', 'Bachelor'),
                    ('master', 'Master'),
                    ('phd', 'PhD'),
                ],
                default='bachelor',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='max_enrollment',
            field=models.PositiveIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='course',
            name='total_semesters',
            field=models.PositiveSmallIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['code']},
        ),
    ]
