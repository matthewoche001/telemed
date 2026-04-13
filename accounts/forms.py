from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class PatientRegistrationForm(UserCreationForm):
    """
    Form for patient self-registration.
    FR-01: User Registration — Role is automatically set to 'patient'.
    """
    full_name = forms.CharField(max_length=255, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "phone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'  # Enforcement of requirement: Registration is for Patients only
        user.first_name = self.cleaned_data['full_name'].split(' ')[0]
        # Store full name in a way that maps to models (AbstractUser has first/last name)
        # But our custom User model doesn't explicitly have 'full_name' field yet, 
        # using 'full_name' as a UI field for now.
        if commit:
            user.save()
        return user
