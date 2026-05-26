from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_shift_and_batch_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shift',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='shift',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='code',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
