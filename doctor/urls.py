# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/prescription/add/<int:patient_id>/', views.add_prescription, name='add_prescription'),
    # Dashboard URLs
    path('doctor/schedule-slots/', views.doctor_schedule_slots, name='doctor_schedule_slots'),
    path('', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('profile/update/', views.update_patient_profile, name='update_patient_profile'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('medical-records/', views.medical_records, name='medical_records'),
    # Doctor-specific URLs
    path('doctor/debug/', views.debug_doctor_names, name='doctor_debug'),
    path('doctor/schedule-appointment/', views.doctor_schedule_appointment, name='doctor_schedule_appointment'),
    path('appointments/schedule/', views.patient_schedule_appointment, name='patient_schedule_appointment'),
    path('patient/<int:patient_id>/details/', views.view_patient_details, name='view_patient_details'),
    path('patient/<int:patient_id>/manage/', views.add_remove_patient, name='add_remove_patient'),
    path('patient/<int:patient_id>/', views.view_patient, name='view_patient'),
    path('patient/<int:patient_id>/prescribe/', views.prescribe_medication, name='prescribe_medication'),
    path('appointment/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
]