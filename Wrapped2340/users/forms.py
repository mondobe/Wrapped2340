from django.contrib.auth.forms import BaseUserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import EmailField, ModelForm, CharField
from django import forms
from .models import Feedback

from Wrapped2340.users.models import UserProfile, Feedback


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

class DeleteAccountForm(forms.Form):
    confirm = CharField(required=False)

    def delete_account(self, user):
        print(self.cleaned_data['confirm'], user.username)
        matches = self.cleaned_data['confirm'] == user.username
        if matches:
            user.delete()
        return matches

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 4}),
        }
        labels = {'message': 'Your Feedback'}
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        # Pass initial values to the form fields
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.username
        self.fields['email'].initial = self.instance.email
        self.fields['first_name'].initial = self.instance.first_name
        self.fields['last_name'].initial = self.instance.last_name
