from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutesettings',
            name='role_channel_access',
            field=models.JSONField(
                default=dict,
                help_text='Role channel defaults. Example: {"student":{"web_portal":true,"mobile_app":true}}',
            ),
        ),
    ]

