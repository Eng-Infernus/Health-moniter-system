from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, Doctor, Appointment, Prescription
from django import forms


# Custom User Creation Form requiring first and last names
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


# Custom User Admin with required names
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')


# Doctor Admin - Doesn't ask for name since using existing user
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'specialty', 'experience']
    search_fields = ['user__first_name', 'user__last_name', 'specialty']

    def get_doctor_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}"

    get_doctor_name.short_description = 'Doctor Name'


# Patient Admin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_emergency_contact', 'get_health_conditions', 'phone_number')
    list_filter = ('blood_type',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'emergency_contact_name')
    readonly_fields = ('user',)

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'date_of_birth', 'blood_type')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Health Information', {
            'fields': ('health_conditions',)
        }),
    )

    def get_patient_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_patient_name.short_description = 'Patient Name'

    def get_emergency_contact(self, obj):
        return obj.get_emergency_contact()

    get_emergency_contact.short_description = 'Emergency Contact'

    def get_health_conditions(self, obj):
        return obj.get_health_conditions()

    get_health_conditions.short_description = 'Health Conditions'


# Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'date_time', 'reason')
    list_filter = ('doctor', 'date_time')
    search_fields = ['patient__user__first_name', 'patient__user__last_name',
                     'doctor__user__first_name', 'doctor__user__last_name']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"

    get_patient_name.short_description = 'Patient'

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"

    get_doctor_name.short_description = 'Doctor'


# Prescription Admin
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_doctor_name', 'medication', 'dosage', 'date_prescribed']
    list_filter = ['doctor', 'date_prescribed']
    search_fields = ['patient__user__first_name', 'patient__user__last_name',
                     'doctor__user__first_name', 'doctor__user__last_name',
                     'medication']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"

    get_patient_name.short_description = 'Patient'

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"

    get_doctor_name.short_description = 'Doctor'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
