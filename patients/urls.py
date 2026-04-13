from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('list/', views.patient_list, name='patient_list'),
    path('profile/', views.patient_edit, name='patient_edit'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
]
