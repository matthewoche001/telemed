from django.db import models
from django.conf import settings
import os

class CTScan(models.Model):
    """
    Table: ct_scans
    FR-07: CT Scan Upload and storage.
    Reference: .agent/ohms.md — Section 6 & 11
    """
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('preprocessing', 'Preprocessing'),
        ('analyzed', 'Analyzed'),
        ('validated', 'Validated'),
        ('failed', 'Failed'),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_scans',
        limit_choices_to={'role': 'patient'},
        help_text="The patient this scan belongs to"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='scans_uploaded_by_staff',
        help_text="User who performed the upload (patient, nurse, or lab_tech)"
    )
    # Using FileField to handle uploads easily
    original_file = models.FileField(
        upload_to='ct_scans/original/',
        max_length=500
    )
    # Path to preprocessed image (result of CNN preprocessing pipeline)
    preprocessed_path = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )

    def __str__(self):
        return f"Scan {self.id} - Patient: {self.patient.username}"

    class Meta:
        db_table = 'ct_scans'
        ordering = ['-upload_timestamp']

    @property
    def filename(self):
        return os.path.basename(self.original_file.name)

class AIResult(models.Model):
    """
    Table: ai_results
    FR-08: AI CT Evaluation; FR-09: AI Validation Dashboard.
    Reference: .agent/ohms.md — Section 6 & 11
    """
    VALIDATION_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('corrected', 'Corrected'),
        ('rejected', 'Rejected'),
    )

    scan = models.OneToOneField(
        CTScan,
        on_delete=models.CASCADE,
        related_name='ai_result'
    )
    predicted_class = models.CharField(
        max_length=20,
        choices=(('normal', 'Normal'), ('abnormal', 'Abnormal'))
    )
    confidence_score = models.FloatField(help_text="0.0 to 1.0")
    ai_timestamp = models.DateTimeField(auto_now_add=True)
    
    validation_status = models.CharField(
        max_length=20,
        choices=VALIDATION_CHOICES,
        default='pending'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_ai_results'
    )
    doctor_notes = models.TextField(blank=True, null=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Result {self.id} for Scan {self.scan.id} - {self.predicted_class}"

    class Meta:
        db_table = 'ai_results'
        ordering = ['-ai_timestamp']
