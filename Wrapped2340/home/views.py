from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView
from ..common import spotifyAPI
from ..users.models import *
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

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