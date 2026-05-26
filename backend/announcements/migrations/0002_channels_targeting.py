from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_shift_and_batch_shift'),
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='channels',
            field=models.JSONField(default=list, help_text='Delivery channels: sms, email, web, mobile'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='target_all_admin_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='announcement',
            name='target_all_students',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='announcement',
            name='target_all_teachers',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='announcement',
            name='target_departments',
            field=models.ManyToManyField(
                blank=True,
                help_text='Faculty / department-wise (students in batches under these departments)',
                related_name='announcements',
                to='students.department',
            ),
        ),
        migrations.AddField(
            model_name='announcement',
            name='target_shifts',
            field=models.ManyToManyField(blank=True, related_name='announcements', to='students.shift'),
        ),
    ]
