from django.contrib.auth.forms import BaseUserCreationForm
from django.forms import EmailField, forms

from Wrapped2340.users.models import UserProfile


class SignUpForm(BaseUserCreationForm):
    email = EmailField(required=True)
    field_order = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=True)
        user.email = self.cleaned_data['email']
        user.save()
        profile = UserProfile.register(user)
        return user

class RotateInviteTokenForm(forms.Form):
    pass