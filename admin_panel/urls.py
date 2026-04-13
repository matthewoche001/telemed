from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('audit-logs/', views.audit_log_view, name='audit_logs'),
    path('audit-logs/export/', views.export_audit_csv, name='export_audit_csv'),
    
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_form, name='staff_add'),
    path('staff/<int:pk>/edit/', views.staff_form, name='staff_edit'),
    
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_form, name='inventory_add'),
    path('inventory/<int:pk>/edit/', views.inventory_form, name='inventory_edit'),
]
