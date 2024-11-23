# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Patient, Doctor, Appointment, Prescription


class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    verbose_name_plural = 'Doctor Information'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user',  'get_emergency_contact', 'get_health_conditions', 'phone_number')
    list_filter = ('blood_type', 'state')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'emergency_contact_name')
    readonly_fields = ('user',)

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'date_of_birth', 'blood_type')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Health Information', {
            'fields': ('health_conditions',)
        }),
    )

    def get_emergency_contact(self, obj):
        return obj.get_emergency_contact()
    get_emergency_contact.short_description = 'Emergency Contact'

    def get_health_conditions(self, obj):
        return obj.get_health_conditions()
    get_health_conditions.short_description = 'Health Conditions'
class CustomUserAdmin(UserAdmin):
    inlines = (DoctorInline,)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# @admin.register(Patient)
# class PatientAdmin(admin.ModelAdmin):
#     list_display = ('user', 'emergency_contact', 'health_conditions')
#     search_fields = ('user__username', 'health_conditions')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'experience')
    search_fields = ('user__username', 'specialty')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date_time', 'reason')
    list_filter = ('doctor', 'date_time')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'medication', 'dosage', 'start_date', 'end_date')
    list_filter = ('doctor', 'start_date')

