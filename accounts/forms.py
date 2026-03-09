from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import BaseUserManager

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        email = BaseUserManager.normalize_email(self.cleaned_data["email"])
        user.email = email
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        max_length=254,
    )
