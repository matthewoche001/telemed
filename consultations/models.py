from django.db import models
from django.conf import settings
from appointments.models import Appointment

class Consultation(models.Model):
    """
    Table: consultations
    FR-04, FR-05: Online Consultation & Clinical Notes.
    Reference: .agent/ohms.md — Section 6 & 11
    """
    STATUS_CHOICES = (
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='consultation'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_consultations'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_consultations'
    )
    notes = models.TextField(blank=True, help_text="Doctor's clinical notes")
    diagnosis = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ongoing'
    )

    def __str__(self):
        return f"Consultation for {self.patient.username} - {self.status}"

    class Meta:
        db_table = 'consultations'

class Prescription(models.Model):
    """
    Table: prescriptions
    FR-05: Digital Prescription issuance.
    Reference: .agent/ohms.md — Section 6
    """
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issued_prescriptions'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_prescriptions'
    )
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication_name} for {self.patient.username}"

    class Meta:
        db_table = 'prescriptions'
