from django.contrib import admin
from .models import UserProfile, Feedback
from Wrapped2340.common.models import Wrapped
from ..common.models import PreviewUrl

admin.site.register(UserProfile)
admin.site.register(Wrapped)
admin.site.register(Feedback)
admin.site.register(PreviewUrl)
