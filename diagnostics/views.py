from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required
from .models import CTScan, AIResult
from .forms import CTScanUploadForm
from .cnn_service import preprocess, predict
from django.utils import timezone
from admin_panel.models import AuditLog
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def log_scan_action(request, action, target_id):
    AuditLog.objects.create(
        user=request.user,
        action=action,
        target_table='ct_scans',
        target_id=target_id,
        ip_address=request.META.get('REMOTE_ADDR')
    )

@login_required
@role_required(['patient', 'nurse', 'lab_tech'])
def upload_scan(request):
    """
    FR-07: CT Scan Upload.
    Access: Patients, nurses, lab_tech only.
    """
    if request.method == 'POST':
        form = CTScanUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            scan = form.save(commit=False)
            scan.uploaded_by = request.user
            
            # If patient is self-uploading, force the patient field
            if request.user.role == 'patient':
                scan.patient = request.user
                
            scan.save()
            log_scan_action(request, 'upload_ct_scan', scan.id)

            # Trigger Preprocessing (Synchronous for now as per Step 7 instructions)
            try:
                scan.status = 'preprocessing'
                scan.save()
                
                # cnn_service.preprocess returns the path to preprocessed image
                p_path = preprocess(scan.original_file.path)
                if p_path:
                    scan.preprocessed_path = p_path
                    scan.status = 'uploaded'
                    scan.save()
                    
                    # --- Trigger CNN Inference (Step 9 Logic) ---
                    try:
                        scan.status = 'analyzed'
                        scan.save()
                        
                        inference_result = predict(scan.preprocessed_path)
                        
                        AIResult.objects.create(
                            scan=scan,
                            predicted_class=inference_result.get('class', 'normal'),
                            confidence_score=inference_result.get('confidence', 0.0)
                        )
                        messages.success(request, f"Scan '{scan.filename}' uploaded and analyzed by AI.")
                    except Exception as ai_e:
                        logger.error(f"AI Inference failed for scan {scan.id}: {str(ai_e)}")
                        scan.status = 'failed'
                        messages.error(request, "Scan uploaded but AI analysis failed.")
                else:
                    scan.status = 'failed'
                    messages.error(request, "Preprocessing failed (format or size issue).")
                scan.save()
            except Exception as e:
                logger.error(f"Preprocessing failed for scan {scan.id}: {str(e)}")
                scan.status = 'failed'
                scan.save()
                messages.error(request, "Scan uploaded but preprocessing failed.")
            
            return redirect('diagnostics:scan_detail', pk=scan.id)
    else:
        form = CTScanUploadForm(user=request.user)
        
    return render(request, 'diagnostics/upload_scan.html', {'form': form})

@login_required
@role_required(['doctor', 'nurse', 'patient', 'admin', 'lab_tech'])
def scan_list(request):
    """
    Role-based scan listing.
    Doctors: see scans for all their patients.
    Patients: see own.
    Admins/Nurses: see all.
    """
    user = request.user
    if user.role == 'patient':
        scans = CTScan.objects.filter(patient=user)
    elif user.role == 'doctor':
        # Doctors see scans for patients they have appointments with
        from appointments.models import Appointment
        patient_ids = Appointment.objects.filter(doctor=user).values_list('patient_id', flat=True)
        scans = CTScan.objects.filter(patient_id__in=patient_ids)
    elif user.role in ['admin', 'nurse']:
        scans = CTScan.objects.all()
    elif user.role == 'lab_tech':
        # Lab tech sees scans they uploaded or all (RBAC says "view assigned scans")
        scans = CTScan.objects.filter(uploaded_by=user)
    else:
        scans = CTScan.objects.none()
        
    return render(request, 'diagnostics/scan_list.html', {'scans': scans})

@login_required
def scan_detail(request, pk):
    scan = get_object_or_404(CTScan, pk=pk)
    user = request.user
    
    # Ownership/Permission Check
    if user.role == 'patient' and scan.patient != user:
        raise PermissionDenied
    
    # Patients can only view own finalized results
    ai_result = None
    if hasattr(scan, 'ai_result'):
        if user.role != 'patient' or scan.ai_result.validation_status != 'pending':
            ai_result = scan.ai_result
            
    return render(request, 'diagnostics/scan_detail.html', {
        'scan': scan,
        'ai_result': ai_result
    })

# ---------------------------------------------------------------------------
# AI Validation Dashboard (Step 10)
# ---------------------------------------------------------------------------

@login_required
@role_required(['doctor'])
def pending_reviews(request):
    """List all scans with validation_status=pending (Doctors only)."""
    results = AIResult.objects.filter(validation_status='pending')
    return render(request, 'diagnostics/pending_reviews.html', {'results': results})

@login_required
@role_required(['doctor'])
def review_detail(request, pk):
    """Doctor reviews AI output vs scan and patient history."""
    result = get_object_or_404(AIResult, pk=pk)
    
    # Visual confidence indicators
    conf = result.confidence_score * 100
    if conf >= 80:
        conf_level = 'high'
    elif conf >= 50:
        conf_level = 'moderate'
    else:
        conf_level = 'low' # Flag for careful review
        
    return render(request, 'diagnostics/review_detail.html', {
        'result': result,
        'conf_percent': round(conf, 1),
        'conf_level': conf_level
    })

@login_required
@role_required(['doctor'])
def validate_result(request, pk):
    """POST handler for doctor validation/correction."""
    result = get_object_or_404(AIResult, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action') # approved, corrected, rejected
        notes = request.POST.get('doctor_notes')
        
        if action in ['approved', 'corrected', 'rejected']:
            result.validation_status = action
            result.doctor = request.user
            result.doctor_notes = notes
            result.validated_at = timezone.now()
            
            if action == 'corrected':
                # Update predicted_class to doctor's correction
                new_class = request.POST.get('corrected_class')
                if new_class in ['normal', 'abnormal']:
                    result.predicted_class = new_class
            
            result.save()
            
            # Update scan status
            result.scan.status = 'validated'
            result.scan.save()
            
            log_scan_action(request, 'validate_ai_result', result.id)
            
            # TODO (FR-13): Notify patient (Step 11)
            messages.success(request, f"Result for Scan {result.scan.id} has been {action}.")
            
    return redirect('diagnostics:pending_reviews')

@login_required
@role_required(['admin'])
def result_history(request):
    """Admin view of all validated results and outcomes."""
    results = AIResult.objects.exclude(validation_status='pending')
    return render(request, 'diagnostics/result_history.html', {'results': results})
