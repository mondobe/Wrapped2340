from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from ..common.models import Wrapped
from ..common.spotifyAPI import get_top_tracks, get_top_genres, get_song_images, get_artist_images, get_top_artists
import json


# Class-based view for slides, with login required
class SlidesView(LoginRequiredMixin, TemplateView):
    template_name = 'slide_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_id = self.kwargs.get('page_id', 1)  # Default to page 1 if not passed

    # Imports wrapped object from id
        wrapped_id = self.kwargs.get('wrapped_id')
        wrapped_object = Wrapped.objects.get(id=wrapped_id)
        userprofile = self.request.user.userprofile
        timeframe = wrapped_object.time_created

        try:
            if page_id == 4:
                top_genres = get_top_genres(userprofile, timeframe)
                print(f"Top Genres: {top_genres}")  # Check the result
                context['top_genres'] = json.dumps(top_genres)
            elif page_id == 6:
                top_songs = get_top_tracks(userprofile, timeframe)
                print(f"Top Songs: {top_songs}")  # Check the result
                context['top_songs'] = get_song_images(top_songs)
            elif page_id == 8:
                top_artists = get_top_artists(userprofile, 10, timeframe)
                print(f"Top Artists: {top_artists}")  # Check the result
                context['top_artists'] = get_artist_images(top_artists)
        except Exception as e:
            print(f"Error fetching data for page {page_id}: {e}")
    # Map page IDs to slide titles or any other data specific to each slide
        slide_titles = {
            1: 'Get Ready to Travel the World with Audioscape 🌎',      # Transition slide
            2: 'Regions Your Favorite Songs are From',                # Info slide
            3: 'Genre-ous Moments Ahead 🎶',            # Transition slide
            4: 'Top Genres',                            # Info slide
            5: 'Counting Down the Beats 🔟',            # Transition slide
            6: 'Top 10 Songs',                          # Info slide
            7: 'Artist Appreciation Time 🎤',           # Transition slide
            8: 'Top Artists',                           # Info slide
            9: 'Pack Your Vibes with Audioscape.AI 🌴',  # Transition slide
            10: 'Your AI Travel Suggestion',            # Info slide
            11: 'Buzzing With Excitement 🐝',           # Transition slide
            12: 'What’s the Buzz? (Game 1)',            # Info slide
            13: '2nd Game intro',                       # Transition slide
            14: 'Game 2',                               # Info slide
        }

        # Set the page title or other context variables based on the page ID
        context['page_title'] = slide_titles.get(page_id, 'Unknown Slide')
        context['page_id'] = page_id  # Pass page_id for navigation
        context['wrapped_object'] = wrapped_object

        return context
