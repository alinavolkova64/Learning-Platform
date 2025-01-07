from django import forms
from .models import FieldOfStudy

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Username', 'class': 'form-control', 'required': True
    }))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'First name', 'class': 'form-control', 'required': True
    }))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Last name', 'class': 'form-control', 'required': True
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email', 'class': 'form-control', 'required': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password', 'class': 'form-control', 'required': True
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password', 'class': 'form-control', 'required': True
    }))
    role = forms.ChoiceField(choices=[('student', 'Student'), ('instructor', 'Instructor')],
                             widget=forms.RadioSelect(attrs={
                                 'class': 'form-group', 'required': True
                             }))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    

class CourseFilterForm(forms.Form):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    level = forms.MultipleChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False  # Allow no selection
    )

    field_of_study = forms.ModelMultipleChoiceField(
        queryset=FieldOfStudy.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False  # Allow no selection
    )
