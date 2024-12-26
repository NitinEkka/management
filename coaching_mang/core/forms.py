from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Course

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Role")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match!")
        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'staff_members']
        widgets = {
            'staff_members': forms.CheckboxSelectMultiple,
        }