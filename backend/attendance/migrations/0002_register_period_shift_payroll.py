# Generated for class register enhancements

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_shift_timing_active'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancesession',
            name='period',
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text='Period number when the same course meets more than once per day (1, 2, …).',
            ),
        ),
        migrations.AddField(
            model_name='attendancesession',
            name='shift',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='attendance_sessions',
                to='students.shift',
            ),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='payroll_exported_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set when this row has been included in a payroll run export.',
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='attendancesession',
            unique_together={('date', 'batch', 'course', 'period')},
        ),
        migrations.AddIndex(
            model_name='attendancesession',
            index=models.Index(fields=['date', 'course'], name='attendance__date_co_idx'),
        ),
    ]
