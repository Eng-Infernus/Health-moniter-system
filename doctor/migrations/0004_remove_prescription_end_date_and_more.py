# Generated by Django 5.1.3 on 2024-11-29 15:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0003_remove_patient_city_remove_patient_state_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='prescription',
            name='start_date',
        ),
        migrations.AddField(
            model_name='prescription',
            name='date_prescribed',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='prescription',
            name='duration',
            field=models.CharField(default='7 days', max_length=100),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='dosage',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='medication',
            field=models.CharField(max_length=200),
        ),
    ]
