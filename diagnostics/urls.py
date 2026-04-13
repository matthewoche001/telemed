from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('upload/', views.upload_scan, name='upload_scan'),
    path('list/', views.scan_list, name='scan_list'),
    path('<int:pk>/', views.scan_detail, name='scan_detail'),

    # AI Validation (Step 10)
    path('pending/', views.pending_reviews, name='pending_reviews'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('validate/<int:pk>/', views.validate_result, name='validate_result'),
    path('history/', views.result_history, name='result_history'),
]
