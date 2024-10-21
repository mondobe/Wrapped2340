from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, View
from .models import *
from ..common import spotifyAPI
from dotenv import load_dotenv
from .forms import SignUpForm

# Loads variables from .env
load_dotenv()

# Create your views here.
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
        return reverse('users:account-settings')

class WrappedLogoutView(LoginRequiredMixin, LogoutView):
    def get_success_url(self):
        referrer = self.request.META.get('HTTP_REFERER')
        if referrer:
            return referrer
        return reverse('users:login')

class AccountSettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'users/account-settings.html'
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    success_url = reverse_lazy('users:account-settings')

    def get_object(self):
        return self.request.user

    def get(self, request):
        if 'code' in request.GET:
            # Extract the code from the URL
            authorization_code = request.GET['code']

            # Grabs tokens
            spotifyAPI.get_access_token(self, authorization_code)
        return super().get(request)

class LinkSpotify(LoginRequiredMixin, View):

    def post(self, request):
        if request.POST.get('action') == 'link':
            url = spotifyAPI.auth()
            return redirect(url)
        return HttpResponse('Invalid action', status=400)

class WrappedPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password-change.html'
    success_url = reverse_lazy('users:account-settings')

class SignUpView(CreateView):
    template_name = 'users/sign-up.html'
    form_class = SignUpForm
    model = User
    success_url = reverse_lazy('users:login')

    def get_object(self):
        return self.request.user
