from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    health_conditions = models.TextField(blank=True, null=True)

    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"

    def get_emergency_contact(self):
        """Returns formatted emergency contact information"""
        if self.emergency_contact_name:
            return f"{self.emergency_contact_name} ({self.emergency_contact_relationship})"
        return "No emergency contact"

    def get_health_conditions(self):
        """Returns health conditions or default message"""
        return self.health_conditions if self.health_conditions else "No health conditions listed"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    experience = models.IntegerField()
    patients = models.ManyToManyField(Patient, related_name='doctors', blank=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True,
                                blank=True)  # Allow null for blocked slots
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)


class Meta:
    ordering = ['date_time']


# models.py
class Prescription(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times', 'Three Times Daily'),
        ('four_times', 'Four Times Daily'),
        ('every_morning', 'Every Morning'),
        ('every_evening', 'Every Evening'),
        ('as_needed', 'As Needed'),
        ('weekly', 'Weekly'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medication = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, choices=FREQUENCY_CHOICES, default='once_daily')
    duration = models.CharField(max_length=100, default="7 days")
    date_prescribed = models.DateTimeField(default=timezone.now)

    @property
    def end_date(self):
        duration_days = int(''.join([c for c in self.duration if c.isdigit()]))
        return self.date_prescribed + timedelta(days=duration_days)

    def __str__(self):
        return f"{self.medication} for {self.patient.user.get_full_name()}"
