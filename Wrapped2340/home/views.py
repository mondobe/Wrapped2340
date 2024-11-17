from os import times
from plistlib import dumps
from string import Formatter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView, View

from .forms import CreateDuoWrappedForm
from ..common import spotifyAPI
from ..common.models import Wrapped
from ..users.models import *
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.userprofile
        context['wraps'] = Wrapped.objects.filter(
            Q(creator1=profile) | Q(creator2=profile)).order_by("-time_created")
        return context

    def post(self, request):
        if request.POST.get('action') == 'newWrap':
            timeframe = request.POST.get('timeframe')
            public = request.POST.get('public') == "true"
            duo = request.POST.get('duo') == "true"
            userprofile = self.request.user.userprofile
            if userprofile.access_token:
                wrapped_content = spotifyAPI.get_wrapped_content(userprofile, timeframe)

                # Create a new Wrapped instance
                new_wrap = Wrapped.objects.create(
                    creator1=userprofile,
                    version='aiden10-30',
                    public=public,
                    content=wrapped_content,
                )
                
                # Redirect to the first slide (page_id 1)
                return redirect('slides:slide', page_id=1)
            else:
                return HttpResponse('Bad Access Token')

        return super().get(request)

class WrappedInviteView(LoginRequiredMixin, TemplateView):
    template_name = 'invite.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            duo1, duo2 = get_duo_users(self.request.user, kwargs['invite_token'])
            context['duo1'] = duo1
            context['duo2'] = duo2
            context['other'] = get_object_or_404(User, userprofile__invite_token=kwargs['invite_token'])
            context['invite_token'] = kwargs['invite_token']
            context['same_user'] = False
        except ValueError:
            context['same_user'] = True
        finally:
            return context

class CreateDuoWrappedView(FormView):
    form_class = CreateDuoWrappedForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        duo1, duo2 = get_duo_users(self.request.user, form.cleaned_data['invite_token'])
        if duo1.userprofile.access_token and duo2.userprofile.access_token:
            wrapped_content = {
                'duo1': spotifyAPI.get_default_wrapped_content(duo1.userprofile),
                'duo2': spotifyAPI.get_default_wrapped_content(duo2.userprofile),
            }

            Wrapped.objects.create(
                creator1=duo1.userprofile,
                creator2=duo2.userprofile,
                version='aiden10-30duo',
                content=wrapped_content,
            )
        else:
            return HttpResponse('Bad Access Token')
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect('home:invite', invite_token=form.cleaned_data['invite_token'])

def get_duo_users(user, other_invite_token):
    username = user.username
    other = get_object_or_404(User, userprofile__invite_token=other_invite_token)

    if other == user:
        raise ValueError("Both users are the same")

    duo1, duo2 = (user, other) \
        if username < other.username \
        else (other, user)

    return duo1, duo2
