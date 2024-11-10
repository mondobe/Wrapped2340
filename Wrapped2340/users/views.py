from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, View, FormView
from .models import *
from ..common import spotifyAPI
from dotenv import load_dotenv
from .forms import SignUpForm, RotateInviteTokenForm, FeedbackForm

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
        return reverse('home:home')

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
            spotifyAPI.get_access_token(self.request.user.userprofile, authorization_code)
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

class WrappedPasswordResetView(PasswordResetView):
    template_name = 'users/password-reset/reset.html'
    email_template_name = 'users/password-reset/email.html'
    subject_template_name = 'users/password-reset/subject.txt'
    success_url = reverse_lazy('users:password-reset-done')

class WrappedPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password-reset/done.html'

class WrappedPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password-reset/confirm.html'
    success_url = reverse_lazy('users:password-reset-complete')

class WrappedPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password-reset/complete.html'

class SignUpView(CreateView):
    template_name = 'users/sign-up.html'
    form_class = SignUpForm
    model = User
    success_url = reverse_lazy('users:login')

    def get_object(self):
        return self.request.user

class RotateInviteTokenView(FormView):
    form_class = RotateInviteTokenForm
    success_url = reverse_lazy('users:account-settings')

    def form_valid(self, form):
        self.request.user.userprofile.rotate_invite_token()
        self.request.user.userprofile.save()
        return super().form_valid(form)


def login_register(request):
    return render(request, 'users/login_register.html', context=None)


def dev_feedback(request):
    # view logic here
    return render(request, 'users/dev-feedback.html')


def manage_feedback(request):
    # view logic here
    return render(request, 'users/manage-feedback.html')

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback_success')
    else:
        form = FeedbackForm()

    return render(request, 'dev-feedback.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def manage_feedback(request):
    if request.method == 'POST':
        feedback_ids = request.POST.getlist('resolved')
        Feedback.objects.filter(id__in=feedback_ids).update(resolved=True)
        Feedback.objects.filter(resolved=True).delete()
        return redirect('manage_feedback')

    feedback_list = Feedback.objects.filter(resolved=False)
    return render(request, 'manage_feedback.html', {'feedback_list': feedback_list})