from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Patient

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
    """
    Requirement: Auto-create a Patient profile when a user registers as a patient.
    """
    if created and instance.role == 'patient':
        Patient.objects.get_or_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_patient_profile(sender, instance, **kwargs):
    """
    Ensures profile is saved when user is saved (if it exists).
    """
    if instance.role == 'patient' and hasattr(instance, 'patient_profile'):
        instance.patient_profile.save()
