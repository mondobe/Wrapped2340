from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

# Separate views for individual pages
def home(request):
    return render(request, 'slides.html', {'page_title': 'Home Page'})

def registered_users(request):
    return render(request, 'slides.html', {'page_title': 'Registered Users'})

def contact_developers(request):
    return render(request, 'slides.html', {'page_title': 'Contact Developers'})

# Class-based view for dynamic slides, with login required
class SlidesView(LoginRequiredMixin, TemplateView):
    template_name = 'slides.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_id = self.kwargs.get('page_id')

        # Map page IDs to slide titles for Top Artists and Top Songs
        slide_titles = {
            1: 'Top Artists',
            2: 'Top Songs',
        }

        # Set the page title based on the page ID
        context['page_title'] = slide_titles.get(page_id, 'Unknown Slide')
        return context
