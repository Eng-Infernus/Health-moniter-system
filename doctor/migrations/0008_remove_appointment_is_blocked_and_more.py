# Generated by Django 5.1.3 on 2024-12-06 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0007_appointment_is_blocked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='is_blocked',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='doctor.patient'),
        ),
    ]