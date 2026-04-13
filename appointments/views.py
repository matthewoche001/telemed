from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required
from .models import Appointment
from .forms import AppointmentBookingForm
from admin_panel.models import AuditLog
from django.contrib import messages

def log_appointment_action(request, action, target_id):
    AuditLog.objects.create(
        user=request.user,
        action=action,
        target_table='appointments',
        target_id=target_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

@login_required
@role_required(['patient'])
def book_appointment(request):
    """
    Patients only: Select doctor and time slot.
    """
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'pending'
            appointment.save()
            
            log_appointment_action(request, 'book_appointment', appointment.id)
            messages.success(request, "Appointment booked successfully. Awaiting confirmation.")
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentBookingForm()
    
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@role_required(['patient', 'doctor', 'nurse', 'admin'])
def appointment_list(request):
    """
    Role-based listing:
    Patients: see own.
    Doctors: see their appointments.
    Admins: see all.
    Nurses: see all (requirement says "Nurses can view appointments").
    """
    user = request.user
    if user.role == 'patient':
        appointments = Appointment.objects.filter(patient=user)
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=user)
    elif user.role in ['admin', 'nurse']:
        appointments = Appointment.objects.all()
    else:
        raise PermissionDenied("Lab Techs do not have access to appointments.")
        
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

@login_required
@role_required(['patient', 'doctor', 'nurse', 'admin'])
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Access check: Patients check own, Doctors check their assigned appt
    if request.user.role == 'patient' and appointment.patient != request.user:
        raise PermissionDenied
    if request.user.role == 'doctor' and appointment.doctor != request.user:
        raise PermissionDenied
        
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})

@login_required
@role_required(['doctor', 'admin'])
def update_appointment_status(request, pk):
    """
    Doctors and Admins only: Update status (confirm, cancel, complete).
    """
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Doctors can only update their own appointments
    if request.user.role == 'doctor' and appointment.doctor != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            log_appointment_action(request, f'status_update_{new_status}', appointment.id)
            messages.success(request, f"Appointment status updated to {new_status}.")
            
    return redirect('appointments:appointment_detail', pk=pk)
