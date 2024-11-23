# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Dashboard URLs
    path('', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('profile/update/', views.update_patient_profile, name='update_patient_profile'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('appointments/schedule/', views.schedule_appointment, name='schedule_appointment'),
    path('medical-records/', views.medical_records, name='medical_records'),
    # Doctor-specific URLs
    path('patient/<int:patient_id>/', views.view_patient, name='view_patient'),
    path('patient/<int:patient_id>/prescribe/', views.prescribe_medication, name='prescribe_medication'),
    path('patient/<int:patient_id>/schedule/', views.schedule_appointment, name='schedule_appointment'),
    path('appointment/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
]