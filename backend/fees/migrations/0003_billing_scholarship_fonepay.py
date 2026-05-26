# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_course_subject'),
        ('students', '0003_shift_timing_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fees', '0002_accounting_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='LateFeePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('grace_days', models.PositiveSmallIntegerField(default=7, help_text='Days after due date before late fee applies')),
                ('rate_percent', models.DecimalField(decimal_places=2, default=2, help_text='Late fee % on outstanding balance', max_digits=5)),
                ('flat_amount', models.DecimalField(decimal_places=2, default=0, help_text='Optional flat late fee (added if > 0)', max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scholarship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('scholarship_type', models.CharField(choices=[('percent', 'Percentage off'), ('fixed', 'Fixed amount off')], default='percent', max_length=20)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('fee_head', models.ForeignKey(blank=True, help_text='Empty = applies to any fee head', null=True, on_delete=models.SET_NULL, related_name='scholarships', to='fees.feehead')),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillingRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_type', models.CharField(choices=[('manual', 'Manual'), ('semester', 'Semester'), ('batch', 'Batch')], default='batch', max_length=20)),
                ('semester', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('completed', 'Completed'), ('failed', 'Failed')], default='completed', max_length=20)),
                ('assignments_created', models.PositiveIntegerField(default=0)),
                ('assignments_skipped', models.PositiveIntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('academic_year', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='billing_runs', to='students.academicyear')),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='billing_runs', to='students.batch')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='billing_runs', to='courses.course')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_runs', to=settings.AUTH_USER_MODEL)),
                ('default_scholarship', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='billing_runs', to='fees.scholarship')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='feestructure',
            name='semester',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Bill this structure for a specific semester', null=True),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='billing_run',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='assignments', to='fees.billingrun'),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='semester',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentfeeassignment',
            name='scholarship',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='assignments', to='fees.scholarship'),
        ),
        migrations.AddField(
            model_name='payment',
            name='gateway_ref',
            field=models.CharField(blank=True, help_text='Fonepay / gateway transaction ID', max_length=200),
        ),
        migrations.AddField(
            model_name='payment',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='payment',
            name='mode',
            field=models.CharField(choices=[('cash', 'Cash'), ('cheque', 'Cheque'), ('esewa', 'eSewa'), ('khalti', 'Khalti'), ('connect_ips', 'Connect IPS'), ('fonepay', 'Fonepay'), ('online', 'Online (other)')], max_length=20),
        ),
    ]
