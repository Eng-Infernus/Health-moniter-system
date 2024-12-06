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
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User


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

    patient = Patient.objects.get_or_create(user=request.user)[0]

    appointments = Appointment.objects.filter(patient=patient).order_by('date_time')
    upcoming_appointments = appointments.filter(date_time__gte=timezone.now())
    past_appointments = appointments.filter(date_time__lt=timezone.now())
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')

    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'prescriptions': prescriptions,
        'is_doctor': False
    }

    return render(request, 'patient_dashboard.html', context)


@login_required
def debug_doctor_names(request):
    doctors = Doctor.objects.all()
    for doctor in doctors:
        print(f"Doctor ID: {doctor.id}")
        print(f"Username: {doctor.user.username}")
        print(f"First Name: {doctor.user.first_name}")
        print(f"Last Name: {doctor.user.last_name}")
        print("---")
    return redirect('doctor_dashboard')


@login_required
# views.py
@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('login')

    patients = doctor.patients.all()
    today = timezone.now()
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        date_time__gte=today
    ).exclude(patient__isnull=True).order_by('date_time')

    # Get available patients but exclude those without names
    available_patients = Patient.objects.exclude(doctors=doctor).exclude(
        user__first_name='',
        user__last_name=''
    ).filter(
        user__first_name__isnull=False,
        user__last_name__isnull=False
    )

    context = {
        'doctor': doctor,
        'patients': patients,
        'upcoming_appointments': upcoming_appointments,
        'all_patients': available_patients
    }
    return render(request, 'doctor_dashboard.html', context)


@login_required
def add_remove_patient(request, patient_id):
    if request.method == 'POST':
        doctor = Doctor.objects.get(user=request.user)
        patient = Patient.objects.get(id=patient_id)
        action = request.POST.get('action')

        if action == 'add':
            doctor.patients.add(patient)
        elif action == 'remove':
            doctor.patients.remove(patient)

        return redirect('doctor_dashboard')


@login_required
def add_prescription(request, patient_id):
    doctor = request.user.doctor
    patient = Patient.objects.get(id=patient_id)
    frequency = Prescription.FREQUENCY_CHOICES
    if request.method == 'POST':
        medication = request.POST.get('medication')
        dosage = request.POST.get('dosage')
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')

        Prescription.objects.create(
            doctor=doctor,
            patient=patient,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            duration=duration
        )
        return redirect('doctor_dashboard')

    return render(request, 'add_prescription.html',
                  {'patient': patient, 'frequency_choices': Prescription.FREQUENCY_CHOICES})


@login_required
def view_patient(request, patient_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return HttpResponseForbidden("Only doctors can access this page.")

    patient = get_object_or_404(Patient, id=patient_id)

    if patient not in doctor.patients.all():
        return HttpResponseForbidden("You don't have permission to view this patient's details.")

    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-date_time')

    prescriptions = Prescription.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-date_prescribed')

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
def view_patient_details(request, patient_id):
    doctor = request.user.doctor
    patient = get_object_or_404(Patient, id=patient_id)
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')
    appointments = Appointment.objects.filter(patient=patient).order_by('-date_time')

    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'appointments': appointments
    }
    return render(request, 'patient_details.html', context)


# views.py
@login_required
def doctor_schedule_slots(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('login')

    time_slots = []
    start_date = timezone.now().date()

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        for hour in range(9, 17):
            slot_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
            time_slots.append({
                'datetime': slot_time,
                'formatted': slot_time.strftime("%Y-%m-%d %H:%M"),
                'is_booked': Appointment.objects.filter(doctor=doctor, date_time=slot_time).exists()
            })

    if request.method == 'POST':
        date_time_str = request.POST.get('date_time')
        try:
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            existing_appt = Appointment.objects.filter(doctor=doctor, date_time=date_time).first()
            if existing_appt:
                existing_appt.delete()
                messages.success(request, 'Time slot freed successfully!')
            else:
                Appointment.objects.create(
                    doctor=doctor,
                    date_time=date_time,
                    reason="BLOCKED"
                )
                messages.success(request, 'Time slot blocked successfully!')
            return redirect('doctor_schedule_slots')
        except Exception as e:
            messages.error(request, str(e))

    context = {
        'time_slots': time_slots,
        'doctor': doctor
    }
    return render(request, 'doctor_schedule_slots.html', context)


@login_required
def doctor_schedule_appointment(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('login')

    patient_id = request.GET.get('patient')
    patient = get_object_or_404(Patient, id=patient_id)

    # Get available slots
    time_slots = []
    start_date = timezone.now().date()

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        for hour in range(9, 17):
            slot_datetime = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
            if not Appointment.objects.filter(doctor=doctor, date_time=slot_datetime).exists():
                time_slots.append({
                    'datetime': slot_datetime,
                    'formatted': slot_datetime.strftime("%Y-%m-%d %H:%M")
                })

    if request.method == 'POST':
        date_time_str = request.POST.get('date_time')
        reason = request.POST.get('reason')

        try:
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date_time=date_time,
                reason=reason
            )
            return redirect('doctor_dashboard')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'schedule_appointment.html', {
        'time_slots': time_slots,
        'patient': patient,
        'doctor': doctor,
        'is_doctor_scheduling': True
    })


@login_required
def patient_schedule_appointment(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        return redirect('register')

    doctors = Doctor.objects.all()
    time_slots = []
    start_date = timezone.now().date()

    for i in range(7):
        current_date = start_date + timedelta(days=i)
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

            if Appointment.objects.filter(doctor=doctor, date_time=date_time).exists():
                messages.error(request, 'This time slot is already booked.')
                return redirect('patient_schedule_appointment')

            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date_time=date_time,
                reason=reason
            )

            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('patient_dashboard')

        except Exception as e:
            messages.error(request, str(e))

    context = {
        'doctors': doctors,
        'time_slots': time_slots,
        'patient': patient,
        'is_doctor_scheduling': False
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

    return render(request, 'update_profile.html', {'patient': patient, 'blood_type_choices': blood_type_choices})


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


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            patient = Patient.objects.create(
                user=user
            )

            login(request, user)  # Auto-login after registration
            messages.success(request, "Registration successful!")
            return redirect('patient_dashboard')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'register.html')

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')
