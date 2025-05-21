from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'rfid_tag', 'role', 'photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'rfid_tag': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    rfid_tag = forms.CharField(label="RFID Tag", max_length=100)