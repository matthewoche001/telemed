from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from .forms import PatientRegistrationForm
from .decorators import role_required

class OHMSLoginView(LoginView):
    """
    Custom Login View with role-based redirection.
    Requirements:
        doctor → /dashboard/doctor/
        nurse → /dashboard/nurse/
        patient → /dashboard/patient/
        admin → /dashboard/admin/
        lab_tech → /dashboard/lab/
    """
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        role_redirects = {
            'doctor': reverse('accounts:doctor_dashboard'),
            'nurse': reverse('accounts:nurse_dashboard'),
            'patient': reverse('accounts:patient_dashboard'),
            'admin': reverse('accounts:admin_dashboard'),
            'lab_tech': reverse('accounts:lab_dashboard'),
        }
        return role_redirects.get(user.role, reverse('accounts:patient_dashboard'))

class OHMSLogoutView(LogoutView):
    """
    Clears session and redirects to login.
    """
    next_page = reverse_lazy('accounts:login')

class PatientRegisterView(CreateView):
    """
    FR-01: Patient self-registration.
    """
    form_class = PatientRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Optional: Auto-login after registration could go here
        return super().form_valid(form)

# ---------------------------------------------------------------------------
# Dashboard Stubs — Protected by login and role checks
# ---------------------------------------------------------------------------

@login_required
@role_required(['doctor'])
def doctor_dashboard(request):
    return render(request, 'accounts/dashboards/doctor.html')

@login_required
@role_required(['nurse'])
def nurse_dashboard(request):
    return render(request, 'accounts/dashboards/nurse.html')

@login_required
@role_required(['patient'])
def patient_dashboard(request):
    return render(request, 'accounts/dashboards/patient.html')

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'accounts/dashboards/admin.html')

@login_required
@role_required(['lab_tech'])
def lab_dashboard(request):
    return render(request, 'accounts/dashboards/lab.html')
