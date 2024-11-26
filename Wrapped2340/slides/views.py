from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from ..common.models import Wrapped
from ..common.spotifyAPI import get_top_tracks


# Class-based view for slides, with login required
class SlidesView(LoginRequiredMixin, TemplateView):
    template_name = 'slide_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_id = self.kwargs.get('page_id')

        # Imports wrapped object from id
        wrapped_id = self.kwargs.get('wrapped_id')
        wrapped_object = Wrapped.objects.get(id=wrapped_id)

        # Fetch top songs for the "Top 10 Songs" slide (page_id = 6)
        if page_id == 6:
            userprofile = self.request.user.userprofile
            timeframe = wrapped_object.timeframe  # Assuming Wrapped model has a timeframe field
            context['top_songs'] = get_top_tracks(userprofile, timeframe)

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
        context['songs'] = wrapped_object.content.get('tracks', [])

        return context
