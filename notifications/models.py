from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Table: notifications
    FR-13: Real-time Alerts & Notifications.
    Reference: .agent/ohms.md — Section 6 & 11
    """
    TYPE_CHOICES = (
        ('appointment', 'Appointment'),
        ('ct_result', 'CT Scan Result'),
        ('consultation', 'Consultation'),
        ('system', 'System'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='system'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:30]}..."

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
