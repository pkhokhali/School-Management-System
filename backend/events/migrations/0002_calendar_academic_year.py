# Generated manually for academic calendar module

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_shift_timing_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendarevent',
            name='academic_year',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='calendar_events',
                to='students.academicyear',
            ),
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='calendar_events_created',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='calendarevent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='event_type',
            field=models.CharField(
                choices=[
                    ('public_holiday', 'Public holiday'),
                    ('holiday', 'Institute holiday'),
                    ('term_break', 'Term break'),
                    ('exam', 'Exam period'),
                    ('event', 'Academic / cultural event'),
                    ('admission', 'Admission'),
                    ('meeting', 'Meeting / assembly'),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name='calendarevent',
            options={'ordering': ['start_date', 'title']},
        ),
        migrations.AddIndex(
            model_name='calendarevent',
            index=models.Index(fields=['academic_year', 'start_date'], name='events_cale_academi_idx'),
        ),
        migrations.AddIndex(
            model_name='calendarevent',
            index=models.Index(fields=['event_type', 'start_date'], name='events_cale_event_t_idx'),
        ),
    ]
