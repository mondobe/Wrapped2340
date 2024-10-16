import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render,redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from . import spotifyAPI
import os
from dotenv import load_dotenv

from .spotifyAPI import client_id

# Loads variables from .env
load_dotenv()

# Create your views here.
def link(request):
    if request.POST.get('action') == 'link':
        print('button clicked')
        url = spotifyAPI.auth()
        return redirect(url)

    if 'code' in request.GET:
        # Extract the code from the URL
        authorization_code = request.GET['code']

        # Grabs tokens
        response_data = spotifyAPI.get_access_token(authorization_code)

        # Gets specific data
        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')

        print(response_data)
        print(access_token)

    return render(request, "users/link.html", context=None)

class WrappedLoginView(LoginView):
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_page = self.request.GET.get('next')
        if next_page:
            context['next_page'] = next_page
        return context

    def get_success_url(self):
        next_page = self.request.GET.get('next')
        if next_page:
            return next_page
        return reverse('urls:account-settings')

class WrappedLogoutView(LoginRequiredMixin, LogoutView):
    def get_success_url(self):
        referrer = self.request.META.get('HTTP_REFERER')
        if referrer:
            return referrer
        return reverse('urls:login')

class AccountSettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'users/account-settings.html'
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    success_url = reverse_lazy('urls:account-settings')

    def get_object(self):
        return self.request.user

class WrappedPasswordChangeView(PasswordChangeView):
    template_name = 'users/password-change.html'
    success_url = reverse_lazy('urls:account-settings')