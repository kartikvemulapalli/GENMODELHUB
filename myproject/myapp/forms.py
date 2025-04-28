from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate

class RegisterForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)  # Add name field
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password']  # Include 'name' in the fields

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Invalid email or password")
        return self.cleaned_data
