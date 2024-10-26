from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from ..common import spotifyAPI
from ..users.models import *
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['duo_invite_link'] = self.request.build_absolute_uri(
            reverse('home:invite',
                    kwargs={'invite_token': self.request.user.userprofile.invite_token})
        )
        return context

    def post(self, request):
        if request.POST.get('action') == 'topArtists':
            access_token = UserProfile.objects.get(user=self.request.user).access_token
            if access_token:
                response = spotifyAPI.get_top_artists(self, access_token, 'medium_term', 10)
                artist_names = [artist.get('name') for artist in response.get('items', [])]
                print(artist_names)
                user = UserProfile.objects.get(user=self.request.user)
                user.add_data_stash(artist_names)
            else:
                return HttpResponse('Bad Access Token')

        return super().get(request)

class WrappedInviteView(LoginRequiredMixin, TemplateView):
    template_name = 'invite.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username

        other_invite_token = kwargs.get('invite_token')
        other = get_object_or_404(User, userprofile__invite_token=other_invite_token)

        if other == self.request.user:
            context['same_user'] = True
            return context
        else:
            context['same_user'] = False

        duo1, duo2 = (self.request.user, other) \
            if username < other.username \
            else (other, self.request.user)

        context['duo1'] = duo1
        context['duo2'] = duo2
        context['other'] = other
        return context