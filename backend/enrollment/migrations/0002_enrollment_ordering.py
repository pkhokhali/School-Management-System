from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enrollment',
            options={'ordering': ['-created_at']},
        ),
    ]
