from django.db import models
from django.conf import settings

class Patient(models.Model):
    """
    Table: patients
    FR-06, FR-15: Patient records and centralized storage.
    Reference: .agent/ohms.md — Section 6
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')), blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    medical_history = models.TextField(blank=True, help_text="Summary of past illnesses, surgeries, allergies")

    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"

    class Meta:
        db_table = 'patients'
