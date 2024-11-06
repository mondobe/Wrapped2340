import base64
import os
import random
import itertools
from datetime import datetime
import re

import requests
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView
from Wrapped2340.common import spotifyAPI
from Wrapped2340 import settings
from Wrapped2340.common.spotifyAPI import get_albums
from Wrapped2340.games import forms
from Wrapped2340.settings import reddit


class WhatsTheBuzzView(FormView):
    form_class = forms.WhatsTheBuzzForm
    template_name = 'games/whats-the-buzz/game.html'

    def form_valid(self, form):
        chosen_artist = form.cleaned_data['chosen_artist']
        correct_hash = form.cleaned_data['correct_hash']
        chosen_hash = get_artist_hash(chosen_artist, self.request.user.userprofile)
        if chosen_hash == correct_hash:
            return redirect('games:whats-the-buzz-correct')
        else:
            return redirect('games:whats-the-buzz-incorrect')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userprofile = self.request.user.userprofile
        random.seed(datetime.now().microsecond)
        top_artists = spotifyAPI.get_top_artists(userprofile, limit=20)
        for i in range(10):
            artist = random.choice(top_artists)
            try:
                real_post_choices = search_reddit(get_search_term(artist), limit=7)
                real_post = random.choice(real_post_choices)
                post_text = real_post.selftext[:400]
                post_text = redact_with_artist(post_text, artist, userprofile)
                post_title = real_post.title
                post_title = redact_with_artist(post_title, artist, userprofile)

                if post_title == '':
                    continue

                context['post_title'] = post_title
                context['post_text'] = post_text

                choices = get_incorrect_choices(artist, top_artists, userprofile)
                correct_index = random.randrange(3)
                choices.insert(correct_index, artist)
                context['choices'] = [c['name'] for c in choices]
                context['correct_hash'] = get_artist_hash(artist['name'], userprofile)
                context['correct_index'] = correct_index

                context['success'] = True
                return context
            except Exception as e:
                continue
        context['success'] = False
        return context

def get_artist_hash(artist_name, userprofile):
    return base64.urlsafe_b64encode(str(hash("%s%s" % (artist_name, userprofile.access_token))).encode('ascii')).decode()

def get_search_term(artist):
    return 'self:true title:"%s" (artist OR band OR album OR song OR topster OR rym) NOT sale' % (artist['name'])

def get_incorrect_choices(artist, top_artists, userprofile):
    related = spotifyAPI.get_related_artists(artist['id'], userprofile)
    related = related[:3]
    other_top_artists = list(filter(lambda a: a != artist and artist not in related, top_artists))
    related[random.randrange(3)] = random.choice(other_top_artists)
    return related

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

class WhatsTheBuzzCorrectView(TemplateView):
    template_name = 'games/whats-the-buzz/correct.html'

class WhatsTheBuzzIncorrectView(TemplateView):
    template_name = 'games/whats-the-buzz/incorrect.html'
