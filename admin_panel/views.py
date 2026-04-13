import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import AuditLog, Inventory
from accounts.models import User
from patients.models import Patient
from appointments.models import Appointment
from diagnostics.models import AIResult
from .forms import StaffForm, InventoryForm

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    """Command Center: KPI Summary and Activity Feed."""
    stats = {
        'total_patients': Patient.objects.count(),
        'active_staff': User.objects.exclude(role='patient').filter(is_active=True).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'pending_ai_reviews': AIResult.objects.filter(validation_status='pending').count(),
    }
    
    # AI Accuracy
    validated = AIResult.objects.exclude(validation_status='pending').count()
    stats['ai_accuracy'] = round((AIResult.objects.filter(validation_status='approved').count() / validated * 100), 1) if validated > 0 else 0
    
    stats['recent_logs'] = AuditLog.objects.all()[:10]
    return render(request, 'admin_panel/dashboard.html', {'stats': stats})

@login_required
@role_required(['admin'])
def staff_list(request):
    staff = User.objects.exclude(role='patient').order_by('role')
    return render(request, 'admin_panel/staff_list.html', {'staff': staff})

@login_required
@role_required(['admin'])
def staff_form(request, pk=None):
    user_obj = get_object_or_404(User, pk=pk) if pk else None
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:staff_list')
    else:
        form = StaffForm(instance=user_obj)
    return render(request, 'admin_panel/staff_form.html', {'form': form, 'edit': pk is not None})

@login_required
@role_required(['admin'])
def inventory_list(request):
    items = Inventory.objects.all()
    return render(request, 'admin_panel/inventory_list.html', {'items': items})

@login_required
@role_required(['admin'])
def inventory_form(request, pk=None):
    item = get_object_or_404(Inventory, pk=pk) if pk else None
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:inventory_list')
    else:
        form = InventoryForm(instance=item)
    return render(request, 'admin_panel/inventory_form.html', {'form': form, 'edit': pk is not None})

@login_required
@role_required(['admin'])
def audit_log_view(request):
    """Searchable/Filterable Audit Log."""
    logs = AuditLog.objects.all()
    
    # Simple filtering
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
        
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
        
    return render(request, 'admin_panel/audit_logs.html', {'logs': logs})

@login_required
@role_required(['admin'])
def export_audit_csv(request):
    """Export all audit logs to CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ohms_audit_log.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Action', 'Target Table', 'Target ID', 'IP Address'])
    
    for log in AuditLog.objects.all():
        writer.writerow([log.timestamp, log.user.username if log.user else 'System', log.action, log.target_table, log.target_id, log.ip_address])
        
    return response
