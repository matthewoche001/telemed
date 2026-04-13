from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required
from .models import Patient
from admin_panel.models import AuditLog
from django.contrib import messages

def log_view(request, action, table, target_id):
    """Ref-06, FR-14: Audit logging helper."""
    AuditLog.objects.create(
        user=request.user,
        action=action,
        target_table=table,
        target_id=target_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

@login_required
@role_required(['doctor', 'nurse', 'admin', 'patient'])
def patient_detail(request, pk):
    """
    View full patient record.
    Access Rules:
    - Doctors, Nurses, Admins: can view any.
    - Patients: can only view own.
    """
    patient = get_object_or_404(Patient, pk=pk)
    
    # Ownership check for patients
    if request.user.role == 'patient' and request.user.patient_profile != patient:
        raise PermissionDenied("You can only view your own record.")
    
    # Requirement: Log all patient record views to audit_logs
    log_view(request, 'view_patient_record', 'patients', patient.id)
    
    return render(request, 'patients/patient_detail.html', {'patient': patient})

@login_required
@role_required(['patient'])
def patient_edit(request):
    """
    Edit own record (patients only).
    Note: Usually pk would be passed, but requirement says "edit own record (patients only)",
    so we fetch the profile from the request.user.
    """
    # Ensure patient has a profile (signal should have created it, but defensive get_or_create)
    patient, created = Patient.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Simple manual update for now or use a ModelForm
        patient.date_of_birth = request.POST.get('date_of_birth') or patient.date_of_birth
        patient.gender = request.POST.get('gender') or patient.gender
        patient.blood_group = request.POST.get('blood_group') or patient.blood_group
        patient.address = request.POST.get('address') or patient.address
        patient.emergency_contact = request.POST.get('emergency_contact') or patient.emergency_contact
        patient.medical_history = request.POST.get('medical_history') or patient.medical_history
        patient.save()
        messages.success(request, "Record updated successfully.")
        return redirect('patients:patient_detail', pk=patient.pk)
        
    return render(request, 'patients/patient_form.html', {'patient': patient})

@login_required
@role_required(['doctor', 'nurse', 'admin'])
def patient_list(request):
    """
    List all patients.
    Access Rules: Doctors, nurses, and admins only.
    """
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})
