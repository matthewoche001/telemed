from django import forms
from accounts.models import User
from .models import Inventory

class StaffForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Admins cannot create patients from this form
        self.fields['role'].choices = [
            choice for choice in User.ROLE_CHOICES if choice[0] != 'patient'
        ]

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'category', 'quantity', 'reorder_threshold']
