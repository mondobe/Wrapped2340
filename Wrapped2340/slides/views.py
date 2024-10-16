from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

class SlidesView(LoginRequiredMixin, TemplateView):
    template_name = 'slides.html'