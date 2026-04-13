from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.OHMSLoginView.as_view(), name='login'),
    path('logout/', views.OHMSLogoutView.as_view(), name='logout'),
    path('register/', views.PatientRegisterView.as_view(), name='register'),

    # Dashboards (Step 3 Requirements)
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/nurse/', views.nurse_dashboard, name='nurse_dashboard'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/lab/', views.lab_dashboard, name='lab_dashboard'),
]
