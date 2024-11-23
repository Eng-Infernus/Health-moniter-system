# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import Patient, Doctor, Appointment, Prescription
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from datetime import date, datetime
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if user is a doctor
            if Doctor.objects.filter(user=user).exists():
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'login.html', context)
    return render(request, 'login.html')


@login_required
def patient_dashboard(request):
    if hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')

    patient, created = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'medical_history': '',
            'emergency_contact': '',
            'health_conditions': ''
        }
    )

    appointments = Appointment.objects.filter(patient=patient).order_by('date_time')
    upcoming_appointments = appointments.filter(date_time__gte=timezone.now())
    past_appointments = appointments.filter(date_time__lt=timezone.now())
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-start_date')

    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'prescriptions': prescriptions,
        'is_doctor': False
    }

    return render(request, 'patient_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('patient_dashboard')

    # Get today's appointments
    today = timezone.now()
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date_time__date=today.date()
    ).order_by('date_time')

    # Get upcoming appointments (excluding today)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        date_time__date__gt=today.date()
    ).order_by('date_time')

    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        doctor=doctor
    ).order_by('-start_date')[:5]

    # Get all patients assigned to this doctor
    patients = doctor.patients.all()

    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_prescriptions': recent_prescriptions,
        'patients': patients,
        'is_doctor': True
    }

    return render(request, 'doctor_dashboard.html', context)


@login_required
def view_patient(request, patient_id):
    # Verify the user is a doctor
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("Only doctors can access this page.")

    patient = get_object_or_404(Patient, id=patient_id)

    # Verify that this patient is assigned to the doctor
    if patient not in doctor.patients.all():
        return HttpResponseForbidden("You don't have permission to view this patient's details.")

    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-date_time')

    prescriptions = Prescription.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-start_date')

    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'is_doctor': True
    }

    return render(request, 'view_patient.html', context)


@login_required
def prescribe_medication(request, patient_id):
    # Verify the user is a doctor
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("Only doctors can prescribe medication.")

    patient = get_object_or_404(Patient, id=patient_id)

    # Verify that this patient is assigned to the doctor
    if patient not in doctor.patients.all():
        return HttpResponseForbidden("You don't have permission to prescribe medication to this patient.")

    if request.method == 'POST':
        try:
            Prescription.objects.create(
                patient=patient,
                doctor=doctor,
                medication=request.POST['medication'],
                dosage=request.POST['dosage'],
                start_date=request.POST['start_date'],
                end_date=request.POST.get('end_date') or None
            )
            messages.success(request, 'Prescription created successfully.')
            return redirect('view_patient', patient_id=patient_id)
        except Exception as e:
            messages.error(request, f'Error creating prescription: {str(e)}')

    context = {
        'patient': patient,
        'is_doctor': True
    }

    return render(request, 'prescribe_medication.html', context)


@login_required
def schedule_appointment(request, patient_id):
    # Verify the user is a doctor
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("Only doctors can schedule appointments.")

    patient = get_object_or_404(Patient, id=patient_id)

    # Verify that this patient is assigned to the doctor
    if patient not in doctor.patients.all():
        return HttpResponseForbidden("You don't have permission to schedule appointments with this patient.")

    if request.method == 'POST':
        try:
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date_time=request.POST['date_time'],
                reason=request.POST['reason'],
                notes=request.POST.get('notes', '')
            )
            messages.success(request, 'Appointment scheduled successfully.')
            return redirect('view_patient', patient_id=patient_id)
        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {str(e)}')

    context = {
        'patient': patient,
        'is_doctor': True
    }

    return render(request, 'schedule_appointment.html', context)


@login_required
def update_appointment(request, appointment_id):
    # Verify the user is a doctor
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("Only doctors can update appointments.")

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if request.method == 'POST':
        try:
            appointment.date_time = request.POST['date_time']
            appointment.reason = request.POST['reason']
            appointment.notes = request.POST.get('notes', '')
            appointment.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('view_patient', patient_id=appointment.patient.id)
        except Exception as e:
            messages.error(request, f'Error updating appointment: {str(e)}')

    context = {
        'appointment': appointment,
        'is_doctor': True
    }

    return render(request, 'update_appointment.html', context)


@login_required
def update_patient_profile(request):
    patient = request.user.patient
    blood_type_choices = Patient.BLOOD_TYPE_CHOICES
    if request.method == 'POST':
        # Update patient information
        patient.phone_number = request.POST.get('phone_number')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.address = request.POST.get('address')
        patient.city = request.POST.get('city')
        patient.state = request.POST.get('state')
        patient.zip_code = request.POST.get('zip_code')
        patient.blood_type = request.POST.get('blood_type')

        # Update emergency contact information
        patient.emergency_contact_name = request.POST.get('emergency_contact_name')
        patient.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        patient.emergency_contact_relationship = request.POST.get('emergency_contact_relationship')

        try:
            patient.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    return render(request, 'update_profile.html', {'patient': patient, 'blood_type_choices':blood_type_choices})


@login_required
def patient_profile(request):
    patient = request.user.patient

    # Calculate age
    today = date.today()
    age = None
    if patient.date_of_birth:
        age = today.year - patient.date_of_birth.year - (
                (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )

    # Get upcoming appointments using date_time field
    upcoming_appointments = patient.appointment_set.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')[:3]

    context = {
        'patient': patient,
        'age': age,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'patient_profile.html', context)


@login_required
def schedule_appointment(request):
    patient = request.user.patient
    doctors = Doctor.objects.all()

    # Generate time slots for the next 7 days
    time_slots = []
    start_date = timezone.now().date()
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        # Generate slots from 9 AM to 5 PM
        for hour in range(9, 17):
            time_slots.append({
                'datetime': datetime.combine(current_date, datetime.min.time().replace(hour=hour)),
                'formatted': datetime.combine(current_date, datetime.min.time().replace(hour=hour)).strftime(
                    "%Y-%m-%d %H:%M")
            })

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_time_str = request.POST.get('date_time')
        reason = request.POST.get('reason')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

            # Check if slot is already booked
            if doctor.appointment_set.filter(date_time=date_time).exists():
                messages.error(request, 'This time slot is already booked. Please choose another.')
                return redirect('schedule_appointment')

            # Create appointment
            appointment = patient.appointment_set.create(
                doctor=doctor,
                date_time=date_time,
                reason=reason
            )

            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('patient_profile')

        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {str(e)}')

    context = {
        'doctors': doctors,
        'time_slots': time_slots,
    }
    return render(request, 'schedule_appointment.html', context)


@login_required
def medical_records(request):
    patient = request.user.patient

    # Get all past appointments
    past_appointments = patient.appointment_set.filter(
        date_time__lt=timezone.now()
    ).order_by('-date_time')

    context = {
        'patient': patient,
        'past_appointments': past_appointments,
    }
    return render(request, 'medical_records.html', context)

@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save()
            # Create a patient profile for the user
            Patient.objects.create(
                user=user,
                medical_history='',
                emergency_contact='',
                health_conditions=''
            )
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')
