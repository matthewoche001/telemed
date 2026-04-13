"""
OHMS Root URL Configuration
All app URLs included here as they are built (Steps 2–16).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    """
    Redirect users hitting the domain root to their specific dashboard based on role.
    """
    if request.user.is_authenticated:
        role_map = {
            'doctor': '/accounts/dashboard/doctor/',
            'nurse': '/accounts/dashboard/nurse/',
            'patient': '/accounts/dashboard/patient/',
            'admin': '/accounts/dashboard/admin/',
            'lab_tech': '/accounts/dashboard/lab/',
        }
        return redirect(role_map.get(request.user.role, '/accounts/login/'))
    return redirect('/accounts/login/')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),

    # Accounts — FR-01, FR-02 (Step 2 & 3)
    path('accounts/', include('accounts.urls')),

    # Patients — FR-06, FR-15 (Step 4)
    path('patients/', include('patients.urls')),

    # Appointments — FR-03 (Step 5)
    path('appointments/', include('appointments.urls')),

    # Consultations — FR-04, FR-05 (Step 6)
    path('consultations/', include('consultations.urls')),

    # Diagnostics / CT Scans / CNN — FR-07, FR-08, FR-09 (Steps 7–10)
    path('diagnostics/', include('diagnostics.urls')),

    # Admin panel — FR-10, FR-11, FR-12 (Steps 12–14)
    path('panel/', include('admin_panel.urls')),

    # Notifications — FR-13 (Step 11)
    path('notifications/', include('notifications.urls')),
]

# Serve media files in development (CT scan uploads)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
