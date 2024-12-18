from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, View, FormView
from .models import *
from ..common import spotifyAPI
from dotenv import load_dotenv
from .forms import RotateInviteTokenForm, FeedbackForm, UserForm, DeleteAccountForm

# Loads variables from .env
load_dotenv()

# Create your views here.
class WrappedLoginView(LoginView):
    template_name = 'users/login_register.html'

    def post(self, request, **kwargs):
        current_tab = request.POST.get('current_tab')
        if request.POST.get('action') == 'Login':
            user = authenticate(request, username=request.POST.get('login-username'), password=request.POST.get('login-password'))

            if user is None:
                # Display an error message if authentication fails (invalid password)
                messages.error(request, "Invalid username or password")
                print("Bad Login")
                return redirect('/users/login')
            else:
                # Log in the user and redirect to the home page upon successful login
                print("Good Login")
                login(request, user)
                return redirect('/home')

        elif request.POST.get('action') == 'register':
            username = request.POST['register-username']
            email = request.POST['register-email']
            password = request.POST['password1']
            password2 = request.POST['password2']
            if password == password2:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username is already taken')
                    print('same username')

                else:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                    )
                    user.userprofile.rotate_invite_token()
                    user.save()
                    print("completed register")
                    return redirect('/users/login')
            else:
                messages.error(request, 'Passwords do not match.')
                print('password no correct')

            return redirect(f'/users/login?tab={current_tab}')


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
    form_class = UserForm
    success_url = reverse_lazy('users:account-settings')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Form is valid, so save the user instance
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'code' in self.request.GET:
            # Extract the code from the URL
            authorization_code = self.request.GET['code']

            # Grabs tokens
            spotifyAPI.get_access_token(self.request.user.userprofile, authorization_code)
        context['duo_invite_link'] = self.request.build_absolute_uri(
            reverse('home:invite',
                    kwargs={'invite_token': self.request.user.userprofile.invite_token})
        )
        return context

class LinkSpotify(LoginRequiredMixin, View):

    def post(self, request):
        if request.POST.get('action') == 'link':
            url = spotifyAPI.auth()
            messages.success(request, 'Account Linked')
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

class RotateInviteTokenView(FormView):
    form_class = RotateInviteTokenForm
    success_url = reverse_lazy('users:account-settings')

    def form_valid(self, form):
        self.request.user.userprofile.rotate_invite_token()
        self.request.user.userprofile.save()
        return super().form_valid(form)

class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = 'users/delete-account.html'
    form_class = DeleteAccountForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        if form.delete_account(self.request.user):
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Assign the logged-in user to the feedback
            feedback.save()  # Save the feedback with the user
            return redirect('users:dev-feedback')
    else:
        form = FeedbackForm()
    return render(request, 'users/dev-feedback.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def manage_feedback(request):
    if request.method == 'POST':
        # Get the list of feedback IDs that are marked as resolved
        resolved_ids = request.POST.getlist('resolved')

        # Delete the feedback items with the selected IDs
        Feedback.objects.filter(id__in=resolved_ids).delete()

        # Redirect to the same page to reflect the changes
        return redirect('users:manage-feedback')

    # Only unresolved feedback for display
    feedback_list = Feedback.objects.filter(resolved=False)

    return render(request, 'users/manage-feedback.html', {'feedback_list': feedback_list})


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
