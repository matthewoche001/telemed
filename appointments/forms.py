from django import forms
from .models import Appointment
from accounts.models import User

class AppointmentBookingForm(forms.ModelForm):
    """
    Form for patients to book appointments.
    Requirements: Select doctor and time slot. Doctor dropdown filtered by role.
    """
    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_at', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Requirement: The doctor dropdown must only show users with role='doctor'
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        # Display full name in dropdown if available
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.get_full_name() or obj.username}"
