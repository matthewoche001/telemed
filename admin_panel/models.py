from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    """
    Table: audit_logs
    FR-14, FR-15: Record auditing and log storage.
    Reference: .agent/ohms.md — Section 6
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who performed the action"
    )
    action = models.CharField(max_length=255, help_text="e.g. 'login', 'view_patient_record'")
    target_table = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

class Inventory(models.Model):
    """
    Table: inventory
    FR-12: Hospital Inventory & Supply Management.
    """
    CATEGORY_CHOICES = (
        ('medical', 'Medical Supplies'),
        ('equipment', 'Clinical Equipment'),
        ('office', 'Office Supplies'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    class Meta:
        db_table = 'inventory'
        verbose_name_plural = "Inventory"
