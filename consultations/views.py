from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from accounts.decorators import role_required
from .models import Consultation, Prescription
from appointments.models import Appointment
from .forms import ConsultationNotesForm, PrescriptionForm
from admin_panel.models import AuditLog
from django.contrib import messages

def log_consult_action(request, action, table, target_id):
    AuditLog.objects.create(
        user=request.user,
        action=action,
        target_table=table,
        target_id=target_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

@login_required
@role_required(['doctor'])
def start_consultation(request, appointment_id):
    """
    Doctor only: Links to an existing 'confirmed' appointment.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    
    # Requirement: Consultation can only be started if the linked appointment status is 'confirmed'
    if appointment.status != 'confirmed':
        messages.error(request, "Consultation can only be started for confirmed appointments.")
        return redirect('appointments:appointment_detail', pk=appointment_id)
    
    # Check if doctor is the one assigned
    if appointment.doctor != request.user:
        raise PermissionDenied("You are not the assigned doctor for this appointment.")

    # Create or get existing consultation
    consultation, created = Consultation.objects.get_or_create(
        appointment=appointment,
        defaults={
            'doctor': appointment.doctor,
            'patient': appointment.patient,
            'status': 'ongoing'
        }
    )
    
    if created:
        log_consult_action(request, 'start_consultation', 'consultations', consultation.id)
        
    return redirect('consultations:consultation_detail', pk=consultation.id)

@login_required
@role_required(['doctor', 'patient', 'nurse', 'admin'])
def consultation_detail(request, pk):
    """
    Detailed consultation view.
    Doctors: Edit notes/diagnosis and add prescriptions.
    Patients: Read-only.
    Nurses: Read-only status.
    """
    consultation = get_object_or_404(Consultation, pk=pk)
    user = request.user

    # RBAC checks
    if user.role == 'patient' and consultation.patient != user:
        raise PermissionDenied
    if user.role == 'doctor' and consultation.doctor != user:
        raise PermissionDenied
    if user.role == 'lab_tech':
        raise PermissionDenied

    notes_form = None
    presc_form = None

    if user.role == 'doctor' and consultation.status == 'ongoing':
        if request.method == 'POST' and 'update_notes' in request.POST:
            notes_form = ConsultationNotesForm(request.POST, instance=consultation)
            if notes_form.is_valid():
                notes_form.save()
                messages.success(request, "Clinical notes updated.")
                return redirect('consultations:consultation_detail', pk=pk)
        else:
            notes_form = ConsultationNotesForm(instance=consultation)
        
        presc_form = PrescriptionForm()

    prescriptions = consultation.prescriptions.all()
    
    return render(request, 'consultations/consultation_detail.html', {
        'consultation': consultation,
        'notes_form': notes_form,
        'presc_form': presc_form,
        'prescriptions': prescriptions
    })

@login_required
@role_required(['doctor'])
def add_prescription(request, consultation_id):
    """Doctor only: adds prescription to active consultation."""
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    if consultation.doctor != request.user or consultation.status != 'ongoing':
        raise PermissionDenied
        
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.consultation = consultation
            prescription.doctor = consultation.doctor
            prescription.patient = consultation.patient
            prescription.save()
            
            log_consult_action(request, 'issue_prescription', 'prescriptions', prescription.id)
            messages.success(request, f"Prescription for {prescription.medication_name} issued.")
            
    return redirect('consultations:consultation_detail', pk=consultation_id)

@login_required
@role_required(['doctor'])
def end_consultation(request, pk):
    """Doctor only: sets status=completed and ended_at=now."""
    consultation = get_object_or_404(Consultation, pk=pk)
    
    if consultation.doctor != request.user:
        raise PermissionDenied
        
    consultation.status = 'completed'
    consultation.ended_at = timezone.now()
    consultation.save()
    
    # Requirement: Update Appointment to completed as well
    consultation.appointment.status = 'completed'
    consultation.appointment.save()
    
    log_consult_action(request, 'end_consultation', 'consultations', consultation.id)
    messages.info(request, "Consultation ended and finalized.")
    
    return redirect('consultations:consultation_detail', pk=pk)

@login_required
@role_required(['doctor', 'patient'])
def prescription_list(request):
    """
    Patients: see own prescriptions.
    Doctors: see issued prescriptions.
    """
    user = request.user
    if user.role == 'patient':
        prescriptions = Prescription.objects.filter(patient=user)
    else:
        prescriptions = Prescription.objects.filter(doctor=user)
        
    return render(request, 'consultations/prescription_list.html', {'prescriptions': prescriptions})
