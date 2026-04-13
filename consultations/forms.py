from django import forms
from .models import Consultation, Prescription

class ConsultationNotesForm(forms.ModelForm):
    """Form for doctors to record notes and diagnosis during consultation."""
    class Meta:
        model = Consultation
        fields = ['notes', 'diagnosis']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Clinical observations...'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Final diagnosis...'}),
        }

class PrescriptionForm(forms.ModelForm):
    """Form for doctors to issue prescriptions."""
    class Meta:
        model = Prescription
        fields = ['medication_name', 'dosage', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }
