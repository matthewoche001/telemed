from django import forms
from .models import CTScan
from accounts.models import User
import os

class CTScanUploadForm(forms.ModelForm):
    """
    Form for uploading CT scan images.
    FR-07: Format validation (DICOM, PNG, JPG).
    """
    class Meta:
        model = CTScan
        fields = ['patient', 'original_file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # If a patient is uploading, fix them as the subject
        if user and user.role == 'patient':
            # self.fields['patient'].initial = user
            # self.fields['patient'].widget = forms.HiddenInput()
            # Or just filter the queryset if staff is uploading
            pass
        self.fields['patient'].queryset = User.objects.filter(role='patient')
        self.fields['patient'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username}"

    def clean_original_file(self):
        file = self.cleaned_data.get('original_file')
        if not file:
            return file

        # 1. Validation: File extension
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = ['.png', '.jpg', '.jpeg', '.dcm']
        if ext not in valid_extensions:
            # Requirement: clear error message
            raise forms.ValidationError("Invalid file format. Please upload PNG, JPG, or DICOM files only.")

        # 2. Validation: File size (20MB)
        if file.size > 20 * 1024 * 1024:
            raise forms.ValidationError("File size exceeds 20MB limit.")

        return file
