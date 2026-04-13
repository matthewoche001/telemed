from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('start/<int:appointment_id>/', views.start_consultation, name='start_consultation'),
    path('<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('<int:consultation_id>/prescribe/', views.add_prescription, name='add_prescription'),
    path('<int:pk>/end/', views.end_consultation, name='end_consultation'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
]
