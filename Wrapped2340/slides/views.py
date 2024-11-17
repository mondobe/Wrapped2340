from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect

from Wrapped2340.common.spotifyAPI import get_top_artists



class SlidesView(LoginRequiredMixin, TemplateView):
    template_name = 'slide_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_id = self.kwargs.get('page_id')

        # Map page IDs to slide titles or any other data specific to each slide
        slide_titles = {
            1: 'Get Ready to Travel the World with Audioscape 🌎',
            2: 'Regions Your Favorite Songs Are From',
            3: 'Genre-ous Moments Ahead 🎶',
            4: 'Top Genres',
            5: 'Counting Down the Beats 🔟',
            6: 'Your Top 10 Songs',
            7: 'Artist Appreciation Time 🎤',
            8: 'Top Artists',
            9: 'Pack Your Vibes with Audioscape.AI 🌴',
            10: 'Your AI Travel Suggestion',
            11: 'Buzzing With Excitement 🐝',
            12: 'What’s the Buzz?',
            13: '2nd Game intro',
            14: 'Game 2',
        }

        context['page_title'] = slide_titles.get(page_id, 'Unknown Slide')
        context['page_id'] = page_id

        # Fetch top artists if on slide 8
        if page_id == 8:
            user_profile = self.request.user.profile
            context['Top Artists'] = get_top_artists(user_profile, 'medium_term')

        return context