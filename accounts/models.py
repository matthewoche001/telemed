from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model for OHMS.
    Reference: .agent/ohms.md — Section 3 (Actors) & Section 6 (Database Schema)
    FR-01: User Registration; FR-02: Authentication
    """
    
    # ENUM choices for roles
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),
        ('lab_tech', 'Lab Technician'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient',
        help_text="Designates the user's role and permissions within the system."
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number (optional)"
    )

    # Use email as unique identifier if needed, but keeping username for default compatibility
    # email = models.EmailField(unique=True) 

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'users'  # Match table name from Section 6 of ohms.md
