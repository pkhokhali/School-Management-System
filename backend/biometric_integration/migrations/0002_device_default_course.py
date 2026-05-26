import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('biometric_integration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='biometricdevice',
            name='default_course',
            field=models.ForeignKey(
                blank=True,
                help_text='Course register to update when webhook does not send course_id.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='biometric_devices',
                to='courses.course',
            ),
        ),
        migrations.AddField(
            model_name='biometricdevice',
            name='default_period',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
