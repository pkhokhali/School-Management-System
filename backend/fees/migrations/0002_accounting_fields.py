# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='cheque_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='payment',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Scholarship / waiver', max_digits=12),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
