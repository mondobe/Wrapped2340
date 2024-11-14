from django.contrib import admin
from .models import UserProfile, Feedback
from Wrapped2340.common.models import Wrapped

admin.site.register(UserProfile)
admin.site.register(Wrapped)
admin.site.register(Feedback)
