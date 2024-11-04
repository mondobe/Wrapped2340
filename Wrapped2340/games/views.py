import os
import random
import itertools
from datetime import datetime
import re

import requests
from django.views.generic import TemplateView
from Wrapped2340.common import spotifyAPI
from Wrapped2340 import settings
from Wrapped2340.common.spotifyAPI import get_albums
from Wrapped2340.settings import reddit


class WhatsTheBuzzView(TemplateView):
    template_name = 'games/whats-the-buzz/game.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for i in range(10):
            random.seed(datetime.now().microsecond)
            artist = random.choice(spotifyAPI.get_top_artists(self.request.user.userprofile))
            try:
                real_post_choices = search_reddit(get_search_term(artist), limit=5)
                real_post = random.choice(real_post_choices)
                post_text = real_post.selftext[:400]
                post_text = redact_with_artist(post_text, artist, self.request.user.userprofile)
                post_title = real_post.title
                post_title = redact_with_artist(post_title, artist, self.request.user.userprofile)

                if post_title == '':
                    continue

                context['post_title'] = post_title
                context['post_text'] = post_text
                context['success'] = True
                return context
            except Exception as e:
                continue
        context['success'] = False
        return context

def get_search_term(artist):
    return 'self:true title:"%s" (artist OR band OR album OR song OR topster OR rym) NOT sale' % (artist['name'])

def search_reddit(query, limit):
    listings = settings.reddit.subreddit('all').search(query, limit=limit)
    return list(listings)

def redact(text, term):
    new_text = text
    regex = re.compile(r'\b%s\b' % re.escape(term), re.IGNORECASE)
    new_text = regex.sub(r'<span class="highlight">[...]</span>', new_text)
    return new_text

allowed_words = ['the', 'a', 'an', 'of', 'my', 'I', 'you', 'your', 'in', 'is', 'back', 'if', 'to']

def redact_with_artist(text, artist, userprofile):
    new_text = text

    albums = spotifyAPI.get_albums(artist['id'], userprofile)
    for album in albums:
        album_title = album['name']
        new_text = redact(new_text, album_title)
        for word in album_title.split(' '):
            if word[0].isupper() and word.lower() not in allowed_words:
                new_text = redact(new_text, word)
    artist_name = artist['name']
    new_text = redact(new_text, artist_name)
    for word in artist_name.split(' '):
        if word.lower() not in allowed_words:
            new_text = redact(new_text, word)

    return new_text