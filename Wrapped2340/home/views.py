from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
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
        context['duo_invite_link'] = self.request.build_absolute_uri(
            reverse('home:invite',
                    kwargs={'invite_token': self.request.user.userprofile.invite_token})
        )
        profile = self.request.user.userprofile
        context['wraps'] = Wrapped.objects.filter(
            Q(creator1=profile) | Q(creator2=profile)).order_by("time_created")
        return context

    def post(self, request):
        if request.POST.get('action') == 'topItems':
            access_token = UserProfile.objects.get(user=self.request.user).access_token
            if access_token:
                artist_response = spotifyAPI.get_top_artists(self, access_token, 'medium_term', 10)
                tracks_response = spotifyAPI.get_top_tracks(self, access_token, 'medium_term', 10)
                artists = {
                    idx: {
                        'name': artist.get('name'),
                        'genres': artist.get('genres',[]),
                    }
                    for idx, artist in enumerate(artist_response.get('items', []))
                }
                tracks = {
                    idx: {
                        'name': track.get('name'),
                        'preview': track.get('preview_url'),
                    }
                    for idx, track in enumerate(tracks_response.get('items', []))
                }
                combined = {
                    idx: {
                        'artist': {
                            'name': artists[idx].get('name'),
                            'genres': artists[idx].get('genres', [])
                        },
                        'track': {
                            'name': tracks[idx].get('name'),
                            'preview_url': tracks[idx].get('preview')
                        }
                    }
                    for idx in range(min(len(artists), len(tracks)))
                }
                print(combined)

                Wrapped.objects.create(
                    creator1=UserProfile.objects.get(user=self.request.user),
                    content=combined,
                )
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