from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allow_mobile_app',
            field=models.BooleanField(
                blank=True,
                help_text='Null = inherit role default; explicit True/False overrides role setting',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='allow_web_portal',
            field=models.BooleanField(
                blank=True,
                help_text='Null = inherit role default; explicit True/False overrides role setting',
                null=True,
            ),
        ),
    ]
