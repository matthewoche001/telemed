from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from appointments.models import Appointment
from diagnostics.models import AIResult, CTScan
from consultations.models import Consultation
from .models import Notification

@receiver(post_save, sender=Appointment)
def notify_appointment_changes(sender, instance, created, **kwargs):
    """
    1. New appointment booked -> notify assigned doctor.
    2. Status confirmed -> notify patient.
    """
    if created:
        Notification.objects.create(
            recipient=instance.doctor,
            message=f"New appointment request from {instance.patient.get_full_name() or instance.patient.username} on {instance.scheduled_at.strftime('%Y-%m-%d %H:%M')}",
            notification_type='appointment',
            link=reverse('appointments:appointment_detail', args=[instance.id])
        )
    else:
        # Check if status changed to confirmed
        # Simple check for demo: if status is confirmed, notify
        if instance.status == 'confirmed':
            Notification.objects.create(
                recipient=instance.patient,
                message=f"Your appointment on {instance.scheduled_at.strftime('%Y-%m-%d %H:%M')} has been confirmed",
                notification_type='appointment',
                link=reverse('appointments:appointment_detail', args=[instance.id])
            )

@receiver(post_save, sender=AIResult)
def notify_ai_result_ready(sender, instance, created, **kwargs):
    """
    3. New AI result (Scan uploaded) -> notify doctor.
    4. Validation complete -> notify patient.
    """
    if created:
        # Identify doctor: notify the doctor currently assigned to the patient's latest confirmed appointment
        latest_appt = Appointment.objects.filter(patient=instance.scan.patient, status='confirmed').first()
        doctor = latest_appt.doctor if latest_appt else None
        
        if doctor:
            Notification.objects.create(
                recipient=doctor,
                message=f"New CT scan uploaded by {instance.scan.patient.username} — pending review",
                notification_type='ct_result',
                link=reverse('diagnostics:review_detail', args=[instance.id])
            )
    else:
        # Validation changed from pending to approved/corrected/rejected
        if instance.validation_status in ['approved', 'corrected']:
            Notification.objects.create(
                recipient=instance.scan.patient,
                message="Your CT scan result is ready. Please log in to view.",
                notification_type='ct_result',
                link=reverse('diagnostics:scan_detail', args=[instance.scan.id])
            )

@receiver(post_save, sender=Consultation)
def notify_consultation_start(sender, instance, created, **kwargs):
    """
    5. Consultation started -> notify patient.
    """
    if created:
        Notification.objects.create(
            recipient=instance.patient,
            message=f"Dr. {instance.doctor.username} has started your consultation",
            notification_type='consultation',
            link=reverse('consultations:consultation_detail', args=[instance.id])
        )
