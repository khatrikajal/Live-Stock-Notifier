from django import forms
from .models import User, StockDetail
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

# User Creation Form (customizing Django's UserCreationForm for your custom User model)
class CustomUserCreationForm(BaseUserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

# User Update Form
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

# Stock Detail Form (for adding or managing stocks)
class StockDetailForm(forms.ModelForm):
    class Meta:
        model = StockDetail
        fields = ['stock', 'users']  # Include 'users' as a Many-to-Many field
